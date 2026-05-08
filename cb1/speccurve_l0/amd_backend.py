from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Any

from .artifacts import read_json
from .benchmark import detect_torch_hardware, run_benchmark
from .pipeline import run_pipeline

ARTIFACT_DIR = Path(os.environ.get("SPECCURVE_ARTIFACT_DIR", "artifacts"))
BACKEND_TOKEN = os.environ.get("SPECCURVE_BACKEND_TOKEN")

try:
    from fastapi import FastAPI, Header, HTTPException
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install AMD backend requirements with `pip install -r requirements-amd.txt`.") from exc

app = FastAPI(title="SpecCurve AMD MI300X Backend", version="0.1.0")


@app.get("/health")
def health() -> dict[str, Any]:
    hardware = detect_torch_hardware()
    benchmark_path = ARTIFACT_DIR / "benchmark.json"
    manifest_path = ARTIFACT_DIR / "run-manifest.json"
    return {
        "service": "speccurve-amd-mi300x-backend",
        "artifact_dir": str(ARTIFACT_DIR),
        "hardware": hardware,
        "has_manifest": manifest_path.exists(),
        "has_benchmark": benchmark_path.exists(),
        "manifest": read_json(manifest_path) if manifest_path.exists() else None,
        "benchmark": read_json(benchmark_path) if benchmark_path.exists() else None,
        "submission_ready": bool(
            benchmark_path.exists()
            and read_json(benchmark_path).get("submission_ready") is True
            and hardware.get("is_mi300x") is True
        ),
    }


@app.post("/run-pipeline")
def run_pipeline_endpoint(
    authorization: Annotated[str | None, Header()] = None,
    source: str = "demo",
    max_specs: int = 96,
) -> dict[str, Any]:
    _require_token(authorization)
    if source not in {"demo", "rdatasets", "nber-dw", "nber-psid"}:
        raise HTTPException(
            status_code=400,
            detail="Remote endpoint allows demo, rdatasets, nber-dw, or nber-psid.",
        )
    result = run_pipeline(
        artifact_dir=ARTIFACT_DIR,
        source=source,
        allow_network=source in {"rdatasets", "nber-dw", "nber-psid"},
        max_specs=max_specs,
    )
    return {
        "dataset_card": result["dataset_card"],
        "spec_batch_id": result["spec_batch_id"],
        "approved_specs": len(result["approved_specs"]),
        "rejected_specs": len(result["rejected_specs"]),
        "results": len(result["results"]),
    }


@app.post("/run-benchmark")
def run_benchmark_endpoint(
    authorization: Annotated[str | None, Header()] = None,
    resamples_per_spec: int = 256,
    spec_limit: int = 64,
) -> dict[str, Any]:
    _require_token(authorization)
    if not (ARTIFACT_DIR / "dataset-card.json").exists():
        run_pipeline(artifact_dir=ARTIFACT_DIR, source="demo", max_specs=max(96, spec_limit))
    return run_benchmark(
        artifact_dir=ARTIFACT_DIR,
        resamples_per_spec=resamples_per_spec,
        spec_limit=spec_limit,
        require_mi300x=True,
    )


def _require_token(authorization: str | None) -> None:
    if not BACKEND_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Set SPECCURVE_BACKEND_TOKEN before enabling write endpoints.",
        )
    expected = f"Bearer {BACKEND_TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid backend token.")
