from __future__ import annotations

import json
import os
import queue
import threading
from pathlib import Path
from typing import Any

from .graph import DEMO_PAPER, run_research_audit
from .model_runtime import runtime_from_env
from .schemas import TraceEvent
from .store import JsonRunStore

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, PlainTextResponse, StreamingResponse
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install API dependencies with `pip install -e .[api]`.") from exc


class RunRequest(BaseModel):
    paper_text: str | None = None
    autonomy_level: int | str = 2
    allow_network: bool | None = None


app = FastAPI(title="Agentic Research Evaluator")
store = JsonRunStore(os.environ.get("RUN_STORE_DIR", "runs"))
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_HTML = PROJECT_ROOT / "index.html"


def _cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "*")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False, response_model=None)
def frontend() -> Any:
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return {"ok": True, "service": "agentic-research-evaluator", "frontend": "index.html missing"}


@app.get("/health")
def health() -> dict[str, Any]:
    runtime_health = runtime_from_env().health()
    return {
        "ok": True,
        "service": "agentic-research-evaluator",
        "model": runtime_health.__dict__,
    }


@app.post("/runs")
def create_run(request: RunRequest) -> dict[str, Any]:
    result = run_research_audit(
        request.paper_text or DEMO_PAPER,
        autonomy_level=request.autonomy_level,
        allow_network=request.allow_network,
    )
    store.save(result)
    return result.to_dict()


@app.post("/runs/stream")
def create_run_stream(request: RunRequest) -> StreamingResponse:
    events: queue.Queue[dict[str, Any] | None] = queue.Queue()

    def on_event(event: TraceEvent) -> None:
        events.put({"event": "trace", "data": event.to_dict()})

    def worker() -> None:
        try:
            result = run_research_audit(
                request.paper_text or DEMO_PAPER,
                autonomy_level=request.autonomy_level,
                allow_network=request.allow_network,
                event_callback=on_event,
            )
            store.save(result)
            events.put({"event": "result", "data": result.to_dict()})
        except Exception as exc:  # pragma: no cover - surfaced to streaming clients
            events.put({"event": "error", "data": {"detail": str(exc)}})
        finally:
            events.put(None)

    threading.Thread(target=worker, daemon=True).start()

    def stream() -> Any:
        while True:
            item = events.get()
            if item is None:
                break
            yield f"event: {item['event']}\ndata: {json.dumps(item['data'])}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    try:
        return store.load(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc


@app.get("/runs/{run_id}/report", response_class=PlainTextResponse)
def get_report(run_id: str) -> str:
    try:
        return store.report(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc
