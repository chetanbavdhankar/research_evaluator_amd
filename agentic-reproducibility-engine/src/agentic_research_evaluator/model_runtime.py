from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class ModelHealth:
    ok: bool
    model_id: str
    base_url: str
    detail: str


class ModelRuntime:
    def health(self) -> ModelHealth:
        raise NotImplementedError

    def chat(self, *, system: str, user: str, temperature: float = 0.0) -> str:
        raise NotImplementedError


class MockModelRuntime(ModelRuntime):
    def __init__(self, model_id: str = "mock-qwen3.5-27b") -> None:
        self.model_id = model_id

    def health(self) -> ModelHealth:
        return ModelHealth(
            ok=True,
            model_id=self.model_id,
            base_url="local-mock",
            detail="deterministic offline runtime",
        )

    def chat(self, *, system: str, user: str, temperature: float = 0.0) -> str:
        del system, temperature
        topic = user.strip().splitlines()[0][:120] if user.strip() else "paper"
        return f"Structured agent note for: {topic}"


class OpenAICompatibleRuntime(ModelRuntime):
    def __init__(
        self,
        base_url: str,
        model_id: str,
        api_key: str = "EMPTY",
        timeout_seconds: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def health(self) -> ModelHealth:
        url = f"{self.base_url}/models"
        request = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
            model_names = [item.get("id") for item in payload.get("data", [])]
            detail = "model listed" if self.model_id in model_names else "endpoint reachable"
            return ModelHealth(True, self.model_id, self.base_url, detail)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            return ModelHealth(False, self.model_id, self.base_url, str(exc))

    def chat(self, *, system: str, user: str, temperature: float = 0.0) -> str:
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers() | {"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}


class GeminiRuntime(ModelRuntime):
    def __init__(
        self,
        api_key: str,
        model_id: str = "gemini-3-flash-preview",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout_seconds: int = 60,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def health(self) -> ModelHealth:
        if not self.api_key:
            return ModelHealth(False, self.model_id, self.base_url, "missing GEMINI_API_KEY")
        try:
            response = self.chat(
                system="Return a short health response.",
                user="Return exactly: ok",
                temperature=0.0,
            )
        except (
            urllib.error.URLError,
            TimeoutError,
            KeyError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            return ModelHealth(False, self.model_id, self.base_url, str(exc))
        detail = "generateContent reachable" if response.strip() else "empty health response"
        return ModelHealth(bool(response.strip()), self.model_id, self.base_url, detail)

    def chat(self, *, system: str, user: str, temperature: float = 0.0) -> str:
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature},
        }
        request = urllib.request.Request(
            f"{self.base_url}/models/{self.model_id}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))
        return _extract_gemini_text(data)


def _extract_gemini_text(data: dict[str, Any]) -> str:
    parts = data["candidates"][0]["content"].get("parts", [])
    return "\n".join(part.get("text", "") for part in parts).strip()


def runtime_from_env() -> ModelRuntime:
    provider = os.environ.get("MODEL_PROVIDER", "").strip().lower()
    if provider == "gemini":
        return GeminiRuntime(
            api_key=os.environ.get("GEMINI_API_KEY", "").strip(),
            model_id=os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview").strip(),
            base_url=os.environ.get(
                "GEMINI_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta",
            ).strip(),
        )

    base_url = os.environ.get("MODEL_BASE_URL", "").strip()
    model_id = os.environ.get("MODEL_NAME", "qwen3.5-27b-amd").strip()
    api_key = os.environ.get("MODEL_API_KEY", "EMPTY")
    if not base_url:
        return MockModelRuntime()
    return OpenAICompatibleRuntime(base_url=base_url, model_id=model_id, api_key=api_key)
