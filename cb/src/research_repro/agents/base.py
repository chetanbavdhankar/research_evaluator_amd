from pydantic import BaseModel
from typing import TypeVar, Type, Tuple
import logging
from research_repro.tools.llm_client import LLMClient
from research_repro.schemas.common import VerificationRecord
from research_repro.agents.verification import deterministic_verify, coherence_verify

T = TypeVar("T", bound=BaseModel)

class BaseAgent:
    def __init__(self, llm_client: LLMClient, role: str):
        self.llm_client = llm_client
        self.role = role
        self.logger = logging.getLogger(f"research_repro.agents.{role}")

    def run_structured(self, prompt: str, response_model: Type[T], source_text: str) -> Tuple[T, VerificationRecord]:
        max_attempts = 3
        last_error = ""
        checks_run = []
        
        messages = [{"role": "user", "content": prompt}]
        
        for attempt in range(max_attempts):
            try:
                # Get structured output
                result = self.llm_client.chat(messages, response_model)
                
                # Layer 1 Verification
                passed, checks, reason = deterministic_verify(result, source_text)
                if not passed:
                    # Layer 2 Fallback Verification
                    passed, l2_checks, reason = coherence_verify(result, source_text, self.llm_client)
                    checks.extend(l2_checks)
                    
                checks_run = list(set(checks_run + checks))
                
                if passed:
                    record = VerificationRecord(
                        checks_run=checks_run,
                        passed=True,
                        attempt_count=attempt + 1,
                    )
                    return result, record
                    
                last_error = reason
                messages.append({"role": "assistant", "content": result.model_dump_json()})
                messages.append({"role": "user", "content": f"Verification failed: {reason}. Please correct the output."})
                
            except Exception as e:
                last_error = str(e)
                messages.append({"role": "user", "content": f"Error: {e}. Try again."})
                
        # Best partial result fallback
        try:
            result = self.llm_client.chat(messages, response_model)
            record = VerificationRecord(
                checks_run=checks_run,
                passed=False,
                attempt_count=max_attempts,
                notes=f"Verification failed after max attempts: {last_error}"
            )
            return result, record
        except Exception as e:
            raise RuntimeError(f"Agent structured run failed after {max_attempts} attempts: {last_error}") from e
