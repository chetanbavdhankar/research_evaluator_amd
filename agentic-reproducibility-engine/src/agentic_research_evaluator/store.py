from __future__ import annotations

import json
from pathlib import Path

from .schemas import RunResult


class JsonRunStore:
    def __init__(self, root: str | Path = "runs") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, result: RunResult) -> None:
        run_dir = self.root / result.manifest.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run.json").write_text(
            json.dumps(result.to_dict(), indent=2),
            encoding="utf-8",
        )
        (run_dir / "report.md").write_text(result.report_markdown, encoding="utf-8")

    def load(self, run_id: str) -> dict:
        path = self.root / run_id / "run.json"
        if not path.exists():
            raise FileNotFoundError(run_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def report(self, run_id: str) -> str:
        path = self.root / run_id / "report.md"
        if not path.exists():
            raise FileNotFoundError(run_id)
        return path.read_text(encoding="utf-8")

