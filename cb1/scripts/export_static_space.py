from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.artifacts import file_hash, read_json, stable_json, write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
SPACE_SRC = ROOT / "space"
ARTIFACTS = ROOT / "artifacts"
EXPORT_DIR = ROOT / "dist" / "hf-static-space-export"
EXPORT_ZIP = ROOT / "dist" / "hf-static-space-export.zip"


def main() -> int:
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    (EXPORT_DIR / "data").mkdir(parents=True)

    shutil.copy2(SPACE_SRC / "README.md", EXPORT_DIR / "README.md")
    shutil.copy2(SPACE_SRC / "index.html", EXPORT_DIR / "index.html")
    shutil.copy2(ARTIFACTS / "surface.svg", EXPORT_DIR / "data" / "surface.svg")

    dataset = read_json(ARTIFACTS / "dataset-card.json")
    baseline = read_json(ARTIFACTS / "baseline.json")
    results = read_json(ARTIFACTS / "result-table.json")
    surface = read_json(ARTIFACTS / "robustness-surface.json")
    approved = read_json(ARTIFACTS / "specs-approved.json")
    rejected = read_json(ARTIFACTS / "specs-rejected.json")
    manifest = read_json(ARTIFACTS / "run-manifest.json")

    write_json(EXPORT_DIR / "data" / "claim.json", _claim_artifact(dataset))
    write_json(EXPORT_DIR / "data" / "baseline.json", baseline)
    write_json(EXPORT_DIR / "data" / "results.json", results)
    write_json(EXPORT_DIR / "data" / "robustness-surface.json", surface)
    write_json(
        EXPORT_DIR / "data" / "specs-sample.json",
        {"approved_sample": approved[:12], "rejected": rejected},
    )
    write_json(EXPORT_DIR / "data" / "status.json", _status_artifact(dataset, manifest, results))

    benchmark_path = ARTIFACTS / "benchmark.json"
    if benchmark_path.exists():
        shutil.copy2(benchmark_path, EXPORT_DIR / "data" / "benchmark.json")
        source_sha = ARTIFACTS / "benchmark.json.sha256"
        if source_sha.exists():
            shutil.copy2(source_sha, EXPORT_DIR / "data" / "benchmark.json.sha256")
        else:
            write_text(
                EXPORT_DIR / "data" / "benchmark.json.sha256",
                f"{file_hash(benchmark_path)}  benchmark.json\n",
            )
        source_hardware_log = ARTIFACTS / "methodology" / "hardware.log"
        if source_hardware_log.exists():
            (EXPORT_DIR / "methodology").mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_hardware_log, EXPORT_DIR / "methodology" / "hardware.log")

    if EXPORT_ZIP.exists():
        EXPORT_ZIP.unlink()
    shutil.make_archive(str(EXPORT_ZIP.with_suffix("")), "zip", EXPORT_DIR)
    _validate_export(EXPORT_DIR)
    print(f"wrote {EXPORT_DIR}")
    print(f"wrote {EXPORT_ZIP}")
    return 0


def _claim_artifact(dataset: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper": "LaLonde 1986; Dehejia and Wahba 1999/2002 data package",
        "dataset_id": dataset["dataset_id"],
        "dataset_source": dataset["source"],
        "dataset_hash": dataset["dataset_hash"],
        "evidence_status": dataset["evidence_status"],
        "row_count": dataset["row_count"],
        "target_claim": (
            "In the NSW job-training design, estimate the ATT of treatment on 1978 real "
            "earnings and inspect whether positive estimates are stable across defensible "
            "matching, weighting, and outcome-model specifications."
        ),
        "outcome": "re78",
        "treatment": "treat",
        "limitations": (
            "This is a public-data specification robustness analysis. It does not independently "
            "repeat the study, settle the paper, or make a final causal-certainty claim."
        ),
        "source_files": dataset.get("source_files", []),
        "warnings": dataset.get("warnings", []),
    }


def _status_artifact(
    dataset: dict[str, Any],
    manifest: dict[str, Any],
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    benchmark_exists = (ARTIFACTS / "benchmark.json").exists()
    return {
        "space_mode": "static",
        "execution_isolation": {
            "server_side_execution": False,
            "user_uploads": False,
            "backend_api_calls": False,
            "user_supplied_code": False,
        },
        "dataset_hash": dataset["dataset_hash"],
        "run_id": manifest.get("run_id"),
        "spec_batch_id": manifest.get("spec_batch_id"),
        "approved_spec_count": manifest.get("approved_spec_count"),
        "rejected_spec_count": manifest.get("rejected_spec_count"),
        "result_count": len(results),
        "benchmark_packaged": benchmark_exists,
        "readiness": "ready" if benchmark_exists else "ready_with_external_blocker",
    }


def _validate_export(path: Path) -> None:
    required = [
        "README.md",
        "index.html",
        "data/claim.json",
        "data/baseline.json",
        "data/results.json",
        "data/robustness-surface.json",
        "data/specs-sample.json",
        "data/status.json",
        "data/surface.svg",
    ]
    missing = [relative for relative in required if not (path / relative).exists()]
    if missing:
        raise RuntimeError(f"static Space export missing files: {', '.join(missing)}")
    readme = (path / "README.md").read_text(encoding="utf-8")
    if "sdk: static" not in readme or "app_file: index.html" not in readme:
        raise RuntimeError("static Space README.md is missing required metadata")
    index = (path / "index.html").read_text(encoding="utf-8")
    forbidden = ["innerHTML", "eval(", "new Function", "fetch('http", 'fetch("http']
    found = [token for token in forbidden if token in index]
    if found:
        raise RuntimeError(f"static Space index.html violates isolation contract: {found}")
    status = read_json(path / "data" / "status.json")
    if status.get("execution_isolation", {}).get("server_side_execution") is not False:
        raise RuntimeError("static Space status.json does not assert server-side isolation")
    if (path / "data" / "benchmark.json").exists():
        benchmark_required = [
            "data/benchmark.json.sha256",
            "methodology/hardware.log",
        ]
        missing_benchmark = [
            relative for relative in benchmark_required if not (path / relative).exists()
        ]
        if missing_benchmark:
            raise RuntimeError(
                "static Space benchmark export missing files: " + ", ".join(missing_benchmark)
            )
    stable_json(status)


if __name__ == "__main__":
    raise SystemExit(main())
