from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def fetch_backend_health(base_url: str, timeout_seconds: float = 4.0) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/health"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return {
            "ok": True,
            "url": url,
            "payload": payload,
            "error": None,
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {
            "ok": False,
            "url": url,
            "payload": None,
            "error": str(exc),
        }
