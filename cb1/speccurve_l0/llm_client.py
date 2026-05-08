from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMConfig:
    endpoint: str
    model: str
    api_key: str
    temperature: float = 0.0
    max_tokens: int = 4096
    timeout_seconds: int = 120

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            endpoint=os.environ.get("SPECCURVE_LLM_ENDPOINT", "http://localhost:11434/v1"),
            model=os.environ.get("SPECCURVE_LLM_MODEL", "qwen3.5:4b"),
            api_key=os.environ.get("SPECCURVE_LLM_API_KEY", "none"),
            temperature=float(os.environ.get("SPECCURVE_LLM_TEMPERATURE", "0")),
            max_tokens=int(os.environ.get("SPECCURVE_LLM_MAX_TOKENS", "4096")),
            timeout_seconds=int(os.environ.get("SPECCURVE_LLM_TIMEOUT_SECONDS", "120")),
        )


class OpenAICompatibleLLMClient:
    """Small OpenAI-compatible chat client for Ollama, vLLM, or hosted APIs."""

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_env()

    def chat_json(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
        max_retries: int = 3,
    ) -> str:
        call_messages = list(messages)
        schema_instruction = (
            "Return only a valid JSON object matching this JSON Schema. "
            "Do not include markdown fences or commentary.\n"
            f"{json.dumps(schema, sort_keys=True)}"
        )
        call_messages.insert(0, {"role": "system", "content": schema_instruction})
        last_error: Exception | None = None
        for attempt in range(max_retries):
            content = self._chat(call_messages, response_format={"type": "json_object"})
            try:
                json.loads(content)
                return content
            except json.JSONDecodeError as exc:
                last_error = exc
                call_messages.append({"role": "assistant", "content": content})
                call_messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous response was not valid JSON. "
                            f"Parser error: {exc}. Return only corrected JSON."
                        ),
                    }
                )
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"LLM did not return valid JSON after {max_retries} attempts: {last_error}")

    def _chat(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None = None,
    ) -> str:
        endpoint = self.config.endpoint.rstrip("/") + "/chat/completions"
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.config.api_key and self.config.api_key.lower() != "none":
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        request = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                response_json = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM endpoint request failed: {exc}") from exc
        choices = response_json.get("choices")
        if not choices:
            raise RuntimeError("LLM response did not include choices")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not content and isinstance(message.get("thinking"), str):
            content = message["thinking"]
        if not isinstance(content, str):
            raise RuntimeError("LLM response did not include text content")
        return _strip_json_fences(content)


def _strip_json_fences(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped
