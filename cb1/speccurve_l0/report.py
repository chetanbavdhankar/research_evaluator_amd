from __future__ import annotations

from typing import Any


def render_report(
    dataset_card: dict[str, Any],
    surface_summary: dict[str, Any],
    approved_specs: list[dict[str, Any]],
    rejected_specs: list[dict[str, Any]],
    baseline: dict[str, Any] | None = None,
    benchmark: dict[str, Any] | None = None,
) -> str:
    dataset_label = dataset_card["dataset_id"]
    warning_lines = "\n".join(f"- {warning}" for warning in dataset_card.get("warnings", []))
    source_file_lines = "\n".join(
        f"- `{source_file['filename']}` from {source_file['url']} "
        f"(sha256 `{source_file['sha256']}`)"
        for source_file in dataset_card.get("source_files", [])
    )
    benchmark_block = _render_benchmark_block(benchmark)
    interpretation_boundary = _interpretation_boundary(dataset_card)
    return f"""# SpecCurve L0 Evidence Report

## Claim Under Test

In a LaLonde-style NSW job-training design, do defensible matching, weighting, and outcome-model specifications estimate a positive ATT for 1978 real earnings, and how stable is that estimate?

## Dataset Card

- Dataset id: `{dataset_label}`
- Dataset hash: `{dataset_card["dataset_hash"]}`
- Row count: {dataset_card["row_count"]}
- Source: {dataset_card["source"]}
- Evidence status: {dataset_card["evidence_status"]}

## Warnings

{warning_lines or "- No dataset warnings recorded."}

## Frozen Source Files

{source_file_lines or "- No frozen raw source files recorded for this run."}

## Verifier Gate

- Approved specifications: {len(approved_specs)}
- Rejected invalid fixtures: {len(rejected_specs)}
- Locked outcome: `re78`
- Locked treatment: `treat`

## Baseline

{_render_baseline_block(baseline)}

## Robustness Surface

- Approved result count: {surface_summary.get("approved_result_count", 0)}
- Headline surface count: {surface_summary.get("surface_result_count", 0)}
- Headline transform: `{surface_summary.get("primary_transform", "n/a")}`
- Minimum estimate: {_fmt(surface_summary.get("min_estimate"))}
- Median estimate: {_fmt(surface_summary.get("median_estimate"))}
- Maximum estimate: {_fmt(surface_summary.get("max_estimate"))}
- Positive estimate share: {_pct(surface_summary.get("positive_share"))}
- CI crosses zero share: {_pct(surface_summary.get("ci_crosses_zero_share"))}
- Estimator levels: {_render_levels(surface_summary.get("estimator_levels", []))}
- Propensity model levels: {_render_levels(surface_summary.get("propensity_model_levels", []))}
- Support rule levels: {_render_levels(surface_summary.get("support_rule_levels", []))}
- Scale note: {surface_summary.get("scale_note", "n/a")}

{benchmark_block}

## Interpretation Boundary

{interpretation_boundary}
"""


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.4f}"


def _pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{100 * float(value):.1f}%"


def _render_levels(values: Any) -> str:
    if not values:
        return "n/a"
    return ", ".join(f"`{value}`" for value in values)


def _render_benchmark_block(benchmark: dict[str, Any] | None) -> str:
    if not benchmark:
        return """## AMD MI300X Benchmark

- Status: no final `benchmark.json` loaded.
- Required next run: execute `python scripts/run_benchmark.py --require-mi300x` on an AMD MI300X ROCm machine and copy the generated artifact into `artifacts/benchmark.json`.
"""

    hardware = benchmark.get("hardware", {})
    return f"""## AMD MI300X Benchmark

- Benchmark id: `{benchmark.get("benchmark_id", "unknown")}`
- GPU: {hardware.get("gpu", "unknown")}
- ROCm/HIP: {hardware.get("hip", "unknown")}
- Scope: {benchmark.get("benchmark_scope", "unknown")}
- CPU runtime seconds: {_fmt(benchmark.get("cpu_runtime_seconds"))}
- GPU runtime seconds: {_fmt(benchmark.get("gpu_runtime_seconds"))}
- Speedup: {_fmt(benchmark.get("speedup"))}x
- Tolerance: {benchmark.get("tolerance_check", {})}
- Tolerance detail: {benchmark.get("tolerance_detail", "n/a")}
- Submission ready: {benchmark.get("submission_ready", False)}
"""


def _render_baseline_block(baseline: dict[str, Any] | None) -> str:
    if not baseline:
        return "- Status: baseline not loaded."
    return f"""- Baseline id: `{baseline.get("baseline_id", "unknown")}`
- Unadjusted ATT: {_fmt(baseline.get("unadjusted_att"))}
- Adjusted ATT: {_fmt(baseline.get("adjusted_att"))}
- Adjusted 95% CI: {_fmt(baseline.get("adjusted_ci_low"))} to {_fmt(baseline.get("adjusted_ci_high"))}
- PSM ATT: {_fmt(baseline.get("matching_att"))}
- PSM 95% CI: {_fmt(baseline.get("matching_ci_low"))} to {_fmt(baseline.get("matching_ci_high"))}
- PSM matched treated rows: {baseline.get("matching_matched_treated", "n/a")}
- Treated/control rows: {baseline.get("treated_count", "n/a")} / {baseline.get("control_count", "n/a")}"""


def _interpretation_boundary(dataset_card: dict[str, Any]) -> str:
    evidence_status = str(dataset_card.get("evidence_status", ""))
    if evidence_status.startswith("frozen_nber_source"):
        return (
            "This run uses frozen NBER LaLonde source files with local hashes. "
            "The empirical interpretation is now tied to those files, but final AMD submission still "
            "requires `benchmark.json` generated on AMD MI300X/ROCm and displayed in the AMD Proof panel."
        )
    return (
        "This L0 build demonstrates the deterministic spine: dataset card, locked claim, spec grid, "
        "verifier, result table, robustness surface, report, and AMD benchmark contract. A public "
        "submission should replace demo or fallback data with the final frozen source files, include "
        "their license/citation trail, and attach a real `benchmark.json` generated on AMD MI300X/ROCm."
    )
