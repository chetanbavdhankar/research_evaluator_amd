import json
import time
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError
from openai import OpenAI
from research_repro.config import AppConfig

logger = logging.getLogger("research_repro.tools.llm_client")

T = TypeVar("T", bound=BaseModel)

class LLMClient:
    def __init__(self, config: AppConfig):
        self.config = config
        # Use LLM_API_KEY from config (defaulting to "none" if empty, per instructions)
        api_key = self.config.model.api_key if self.config.model.api_key and self.config.model.api_key.lower() != "none" else "none"
        self.client = OpenAI(
            base_url=self.config.model.endpoint,
            api_key=api_key,
        )

    def chat(self, messages: List[Dict[str, str]], response_model: Optional[Type[T]] = None) -> Union[T, str]:
        start_time = time.time()
        
        # Prepare messages
        call_messages = list(messages)
        
        if response_model is not None:
            # Inject schema into system prompt or user prompt
            schema_json = json.dumps(response_model.model_json_schema())
            instruction = f"\n\nYou must respond with a valid JSON object matching this schema:\n{schema_json}"
            
            # Find system message to append to, or add one
            system_msg_idx = next((i for i, m in enumerate(call_messages) if m["role"] == "system"), -1)
            if system_msg_idx >= 0:
                call_messages[system_msg_idx] = {
                    "role": "system",
                    "content": call_messages[system_msg_idx]["content"] + instruction
                }
            else:
                call_messages.insert(0, {"role": "system", "content": instruction})

        max_retries = 3 if response_model else 1
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Add response_format parameter if response_model is used
                # Note: vLLM and Ollama support format="json" or response_format={"type": "json_object"}
                kwargs: Dict[str, Any] = {
                    "model": self.config.model.model,
                    "messages": call_messages,
                    "temperature": self.config.model.temperature,
                    "max_tokens": self.config.model.max_tokens,
                }
                
                if response_model is not None:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = self.client.chat.completions.create(**kwargs)
                
                message = response.choices[0].message
                content = message.content
                
                # Handling Qwen thinking output quirk
                if not content and hasattr(message, 'model_extra') and message.model_extra and 'thinking' in message.model_extra:
                    content = message.model_extra['thinking']
                    
                if not content:
                    content = ""
                
                latency = time.time() - start_time
                usage = response.usage
                tokens_info = f"prompt={usage.prompt_tokens} completion={usage.completion_tokens} total={usage.total_tokens}" if usage else "usage=unknown"
                logger.info(f"{latency:.2f}s [LLM Call] attempt={attempt+1} {tokens_info}")
                
                if response_model is None:
                    return content
                
                try:
                    # Parse and validate JSON
                    parsed_json = json.loads(content)
                    return response_model.model_validate(parsed_json)
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.warning(f"Failed to parse LLM output (attempt {attempt+1}/{max_retries}): {e}")
                    last_error = e
                    # Inject failure reason into next attempt
                    call_messages.append({"role": "assistant", "content": content})
                    call_messages.append({
                        "role": "user",
                        "content": f"Your previous response failed validation with the following error:\n{e}\n\nPlease fix the JSON and try again. Remember to only output valid JSON matching the schema."
                    })
            except Exception as e:
                logger.error(f"API call failed: {e}")
                last_error = e
                # Wait before retry for API errors
                time.sleep(2 ** attempt)

        logger.error(f"Exhausted {max_retries} retries.")
        raise last_error or RuntimeError("LLM call failed without a specific error.")
