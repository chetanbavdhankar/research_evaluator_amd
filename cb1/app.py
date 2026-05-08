from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from speccurve_l0.agentic_planner import plan_reproduction_workflow
from speccurve_l0.agentic_verifier import verify_reproduction_plan
from speccurve_l0.artifacts import read_json
from speccurve_l0.benchmark import detect_torch_hardware
from speccurve_l0.llm_client import OpenAICompatibleLLMClient
from speccurve_l0.pipeline import run_pipeline
from speccurve_l0.remote import fetch_backend_health
from speccurve_l0.report import render_report

ARTIFACT_DIR = Path(os.environ.get("SPECCURVE_ARTIFACT_DIR", "artifacts"))
DEMO_ARTIFACT_DIR = Path(
    os.environ.get(
        "SPECCURVE_DEMO_ARTIFACT_DIR",
        str(ARTIFACT_DIR.parent / f"{ARTIFACT_DIR.name}-demo"),
    )
)
DEFAULT_AMD_BACKEND_URL = "http://165.245.141.127:8000"
AMD_BACKEND_URL = os.environ.get("AMD_BACKEND_URL", DEFAULT_AMD_BACKEND_URL).strip()


def _load_report() -> tuple[str, str, dict[str, Any], list[list[Any]]]:
    if not (ARTIFACT_DIR / "report.md").exists():
        return _run_demo()

    report = (ARTIFACT_DIR / "report.md").read_text(encoding="utf-8")
    surface_svg = (ARTIFACT_DIR / "surface.svg").read_text(encoding="utf-8")
    surface_summary = read_json(ARTIFACT_DIR / "robustness-surface.json")
    rows = _result_rows(read_json(ARTIFACT_DIR / "result-table.json"))
    return report, surface_svg, surface_summary, rows


def _run_demo() -> tuple[str, str, dict[str, Any], list[list[Any]]]:
    result = run_pipeline(DEMO_ARTIFACT_DIR, source="demo", max_specs=240)
    return (
        result["report"],
        result["surface_svg"],
        result["surface_summary"],
        _result_rows(result["results"]),
    )


def _amd_panel() -> str:
    benchmark_path = ARTIFACT_DIR / "benchmark.json"
    hardware = detect_torch_hardware()
    if benchmark_path.exists():
        benchmark = read_json(benchmark_path)
        return render_report(
            read_json(ARTIFACT_DIR / "dataset-card.json"),
            read_json(ARTIFACT_DIR / "robustness-surface.json"),
            read_json(ARTIFACT_DIR / "specs-approved.json"),
            read_json(ARTIFACT_DIR / "specs-rejected.json"),
            baseline=read_json(ARTIFACT_DIR / "baseline.json"),
            benchmark=benchmark,
        )

    remote_block = ""
    if AMD_BACKEND_URL:
        health = fetch_backend_health(AMD_BACKEND_URL)
        if health["ok"]:
            payload = health["payload"]
            remote_block = f"""
## Live AMD Backend

- URL: `{health["url"]}`
- MI300X detected: `{payload.get("hardware", {}).get("is_mi300x")}`
- GPU: `{payload.get("hardware", {}).get("gpu")}`
- HIP/ROCm: `{payload.get("hardware", {}).get("hip")}`
- Benchmark loaded: `{payload.get("has_benchmark")}`
- Submission ready: `{payload.get("submission_ready")}`
"""
        else:
            remote_block = f"""
## Live AMD Backend

- URL: `{health["url"]}`
- Status: unreachable from this Space/runtime.
- Error: `{health["error"]}`
"""

    return f"""# AMD MI300X Proof Panel

No final `artifacts/benchmark.json` is loaded yet.

Detected runtime:

```json
{hardware}
```

Final submission path:

1. Run the deterministic pipeline on the frozen dataset.
2. On an AMD MI300X ROCm host, execute `python scripts/run_benchmark.py --require-mi300x`.
3. Copy `artifacts/benchmark.json` and `artifacts/benchmark.json.sha256` into the hosted Space.

The Hugging Face Space is the hosted webapp surface. The MI300X proof is the benchmark artifact generated on AMD hardware.

{remote_block}
"""


def _result_rows(results: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            result["spec_id"],
            round(float(result["estimate_att"]), 4),
            round(float(result["ci_low"]), 4),
            round(float(result["ci_high"]), 4),
            result["n"],
            result["outcome_transform"],
            result["sample_filter"],
            result["estimator"],
            result.get("propensity_model", "none"),
            result.get("support_rule", "none"),
        ]
        for result in results
    ]


def _plan_workflow_from_text(paper_text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not paper_text.strip():
        return {}, {
            "passed": False,
            "score": 0.0,
            "checks": [],
            "failures": ["paper text is required"],
            "warnings": [],
        }
    try:
        plan = plan_reproduction_workflow(paper_text, OpenAICompatibleLLMClient())
        verification = verify_reproduction_plan(plan, paper_text)
        return plan.to_dict(), verification.to_dict()
    except Exception as exc:
        return {}, {
            "passed": False,
            "score": 0.0,
            "checks": [],
            "failures": [str(exc)],
            "warnings": ["Check SPECCURVE_LLM_ENDPOINT, SPECCURVE_LLM_MODEL, and endpoint reachability."],
        }


try:
    import gradio as gr
except ImportError as exc:  # pragma: no cover - exercised only outside HF/local deps
    raise SystemExit(
        "Gradio is not installed. Run `pip install -r requirements.txt` for the webapp, "
        "or run `python scripts/run_pipeline.py` to verify the deterministic core."
    ) from exc


INITIAL_REPORT, INITIAL_SURFACE, INITIAL_SUMMARY, INITIAL_TABLE = _load_report()
INITIAL_AMD_PANEL = _amd_panel()


with gr.Blocks(title="SpecCurve L0 AMD MI300X Evidence Lab") as demo:
    gr.Markdown(
        "# SpecCurve L0 AMD MI300X Evidence Lab\n"
        "Deterministic Wiki C spine with a Hugging Face-hosted interface and a separate "
        "ROCm/MI300X benchmark artifact path."
    )
    with gr.Tabs():
        with gr.Tab("Report"):
            report = gr.Markdown(value=INITIAL_REPORT)
            reload_button = gr.Button("Load current artifacts")
        with gr.Tab("Run Pipeline"):
            gr.Markdown(
                "Runs the synthetic demo fixture in an isolated demo artifact folder. This does not "
                "replace the frozen NBER evidence artifacts shown in the main report."
            )
            run_button = gr.Button("Run isolated demo pipeline")
            summary = gr.JSON(value=INITIAL_SUMMARY, label="Robustness summary")
        with gr.Tab("Agent Planner"):
            gr.Markdown(
                "Paste extracted paper text. The LLM proposes a reproduction workflow; the verifier "
                "scores whether the plan is grounded and executable before any code path is trusted."
            )
            paper_text = gr.Textbox(label="Paper text", lines=12)
            plan_button = gr.Button("Construct verified workflow")
            workflow_plan = gr.JSON(label="workflow-plan.json")
            verification_report = gr.JSON(label="verification-report.json")
        with gr.Tab("Surface"):
            surface = gr.HTML(value=INITIAL_SURFACE)
            table = gr.Dataframe(
                value=INITIAL_TABLE,
                headers=[
                    "spec_id",
                    "estimate_att",
                    "ci_low",
                    "ci_high",
                    "n",
                    "transform",
                    "filter",
                    "estimator",
                    "propensity_model",
                    "support_rule",
                ],
                datatype=[
                    "str",
                    "number",
                    "number",
                    "number",
                    "number",
                    "str",
                    "str",
                    "str",
                    "str",
                    "str",
                ],
                interactive=False,
            )
        with gr.Tab("AMD Proof"):
            amd_panel = gr.Markdown(value=INITIAL_AMD_PANEL)
            amd_button = gr.Button("Refresh AMD proof panel")

    reload_button.click(_load_report, outputs=[report, surface, summary, table])
    run_button.click(_run_demo, outputs=[report, surface, summary, table])
    plan_button.click(_plan_workflow_from_text, inputs=[paper_text], outputs=[workflow_plan, verification_report])
    amd_button.click(_amd_panel, outputs=[amd_panel])


if __name__ == "__main__":
    demo.launch(server_port=int(os.environ.get("SPECCURVE_PORT", "7860")))
