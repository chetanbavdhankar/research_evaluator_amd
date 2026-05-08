from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.agentic_planner import plan_reproduction_workflow
from speccurve_l0.agentic_verifier import verify_reproduction_plan
from speccurve_l0.artifacts import write_json
from speccurve_l0.llm_client import OpenAICompatibleLLMClient


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ask an LLM agent to construct a verifiable reproduction workflow for a paper."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--paper-text", type=Path, help="Path to extracted paper text.")
    source.add_argument("--paper-url", help="URL containing paper text or HTML.")
    parser.add_argument("--output-dir", type=Path, default=Path("agent-runs/latest"))
    args = parser.parse_args()

    paper_text = _load_paper_text(args.paper_text, args.paper_url)
    client = OpenAICompatibleLLMClient()
    plan = plan_reproduction_workflow(paper_text, client)
    verification = verify_reproduction_plan(plan, paper_text)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "workflow-plan.json", plan.to_dict())
    write_json(args.output_dir / "verification-report.json", verification.to_dict())
    print(json.dumps({"verification": verification.to_dict(), "output_dir": str(args.output_dir)}, indent=2))
    return 0 if verification.passed else 1


def _load_paper_text(path: Path | None, url: str | None) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")
    if url is None:
        raise ValueError("one paper source is required")
    request = urllib.request.Request(url, headers={"User-Agent": "SpecCurve-Agent/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content_type = response.headers.get("content-type", "")
        raw = response.read()
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        raise ValueError("PDF parsing is not built into this L0 planner. Provide extracted text with --paper-text.")
    return raw.decode("utf-8", errors="replace")


if __name__ == "__main__":
    raise SystemExit(main())
