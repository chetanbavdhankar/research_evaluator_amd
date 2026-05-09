from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    log_path = project_root / "uvicorn.combined.log"
    os.chdir(project_root)

    with log_path.open("a", encoding="utf-8") as log:
        sys.stdout = log
        sys.stderr = log
        try:
            import uvicorn

            uvicorn.run(
                "agentic_research_evaluator.api:app",
                host="127.0.0.1",
                port=8080,
                log_level="info",
            )
        except Exception:
            traceback.print_exc()
            raise


if __name__ == "__main__":
    main()
