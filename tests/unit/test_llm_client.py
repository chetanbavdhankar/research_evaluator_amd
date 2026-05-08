import pytest
import httpx
from pydantic import BaseModel
from research_repro.tools.llm_client import LLMClient
from research_repro.config import AppConfig

class DummyResponse(BaseModel):
    ok: bool

def test_llm_client_chat_json(httpx_mock):
    config = AppConfig(
        llm_endpoint="http://dummy:8000/v1",
        llm_model="qwen3.5:4b",
        llm_api_key="none"
    )
    client = LLMClient(config)
    
    # Mock successful JSON response
    httpx_mock.add_response(
        json={
            "choices": [
                {
                    "message": {
                        "content": '{"ok": true}'
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
    )
    
    result = client.chat([{"role": "user", "content": "hello"}], response_model=DummyResponse)
    
    assert isinstance(result, DummyResponse)
    assert result.ok is True

def test_llm_client_retry_on_invalid_json(httpx_mock):
    config = AppConfig(
        llm_endpoint="http://dummy:8000/v1",
        llm_model="qwen3.5:4b",
        llm_api_key="none"
    )
    client = LLMClient(config)
    
    # First response is invalid JSON
    httpx_mock.add_response(
        json={
            "choices": [
                {
                    "message": {
                        "content": '{"ok": '  # Malformed
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
    )
    
    # Second response is valid JSON
    httpx_mock.add_response(
        json={
            "choices": [
                {
                    "message": {
                        "content": '{"ok": true}'
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
    )
    
    result = client.chat([{"role": "user", "content": "hello"}], response_model=DummyResponse)
    
    assert isinstance(result, DummyResponse)
    assert result.ok is True
    # Verify two requests were made
    assert len(httpx_mock.get_requests()) == 2
