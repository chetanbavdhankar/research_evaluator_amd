from __future__ import annotations

import os


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Install API dependencies with `pip install -e .[api]`.") from exc

    uvicorn.run(
        "agentic_research_evaluator.api:app",
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8080")),
        reload=os.environ.get("RELOAD", "0") == "1",
    )


if __name__ == "__main__":
    main()
