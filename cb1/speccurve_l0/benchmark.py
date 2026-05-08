from __future__ import annotations

import platform
import time
from pathlib import Path
from typing import Any

from .analysis import apply_filter, design_matrix
from .artifacts import read_json, stable_hash, utc_now, write_json
from .benchmark_contract import write_benchmark_sha256, write_hardware_log
from .data import load_lalonde_csv


def detect_torch_hardware() -> dict[str, Any]:
    try:
        import torch
    except ImportError:
        return {
            "torch_available": False,
            "cpu": "unknown",
            "gpu": None,
            "rocm": None,
            "torch": None,
            "hip": None,
            "is_mi300x": False,
        }

    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    hip_version = getattr(torch.version, "hip", None)
    cpu_label = platform.processor() or platform.machine() or "unknown CPU"
    return {
        "torch_available": True,
        "cpu": f"{cpu_label} ({platform.platform()})",
        "gpu": gpu_name,
        "rocm": hip_version,
        "torch": torch.__version__,
        "hip": hip_version,
        "is_mi300x": bool(gpu_name and "MI300" in gpu_name.upper()),
    }


def run_benchmark(
    artifact_dir: Path,
    resamples_per_spec: int = 64,
    spec_limit: int = 24,
    require_mi300x: bool = True,
    output_name: str = "benchmark.json",
) -> dict[str, Any]:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("PyTorch is required for the AMD benchmark path") from exc

    hardware = detect_torch_hardware()
    if require_mi300x and not hardware["is_mi300x"]:
        raise RuntimeError(
            "AMD MI300X was required but not detected. Run on a ROCm-enabled MI300X host."
        )
    if not torch.cuda.is_available():
        raise RuntimeError("No GPU device is available to PyTorch")

    dataset_path = artifact_dir / "data" / "dataset.csv"
    specs_path = artifact_dir / "specs-approved.json"
    dataset_card = read_json(artifact_dir / "dataset-card.json")
    rows = load_lalonde_csv(dataset_path)
    approved_specs = read_json(specs_path)
    specs = [
        spec for spec in approved_specs if spec.get("estimator") in {"ols", "ridge_1e-6"}
    ][:spec_limit]
    if not specs:
        raise RuntimeError("No approved linear specs are available for benchmark")

    cpu_results, cpu_runtime = _measure_device(torch, rows, specs, resamples_per_spec, "cpu")
    gpu_results, gpu_runtime = _measure_device(torch, rows, specs, resamples_per_spec, "cuda")
    max_abs_diff = max(abs(a - b) for a, b in zip(cpu_results, gpu_results, strict=True))
    passed = max_abs_diff <= 1e-3
    total_runs = len(specs) * resamples_per_spec
    benchmark = {
        "benchmark_id": f"speccurve-l0-mi300x-{utc_now()}",
        "dataset_hash": dataset_card["dataset_hash"],
        "spec_batch_id": stable_hash([spec["spec_id"] for spec in specs])[:16],
        "approved_spec_count": len(specs),
        "benchmark_scope": "approved linear outcome-model specs from the Wiki C grid",
        "excluded_estimator_levels": sorted(
            {
                str(spec.get("estimator"))
                for spec in approved_specs
                if spec.get("estimator") not in {"ols", "ridge_1e-6"}
            }
        ),
        "resamples_per_spec": resamples_per_spec,
        "total_statistical_runs": total_runs,
        "cpu_runtime_seconds": cpu_runtime,
        "gpu_runtime_seconds": gpu_runtime,
        "speedup": cpu_runtime / gpu_runtime if gpu_runtime else None,
        "throughput_cpu": total_runs / cpu_runtime if cpu_runtime else None,
        "throughput_gpu": total_runs / gpu_runtime if gpu_runtime else None,
        "tolerance_check": "pass" if passed else "fail",
        "tolerance_detail": {
            "max_abs_diff": max_abs_diff,
            "passed": passed,
            "threshold": 1e-3,
        },
        "warmup_policy": "One unrecorded batched bootstrap pass per device before timing.",
        "hardware": {
            "cpu": hardware["cpu"],
            "gpu": hardware["gpu"],
            "rocm": hardware["rocm"],
            "torch": hardware["torch"],
            "hip": hardware["hip"],
            "is_mi300x": hardware["is_mi300x"],
        },
        "generated_at": utc_now(),
        "_status": "APPROVED" if hardware["is_mi300x"] and passed else "REJECTED",
        "provenance": {
            "generated_by": "scripts/run_benchmark.py",
            "seed": "torch.Generator(device='cpu').manual_seed(7000 + spec_index)",
            "source": "speccurve-wiki/09-gpu-and-benchmark-contract.md",
        },
        "submission_ready": bool(hardware["is_mi300x"] and passed),
    }
    benchmark_path = artifact_dir / output_name
    write_json(benchmark_path, benchmark)
    write_benchmark_sha256(benchmark_path)
    write_hardware_log(artifact_dir, benchmark, hardware, benchmark_path)
    return benchmark


def _measure_device(
    torch: Any,
    rows: list[dict[str, float]],
    specs: list[dict[str, Any]],
    resamples_per_spec: int,
    device: str,
) -> tuple[list[float], float]:
    _run_device(torch, rows, specs[:1], min(2, resamples_per_spec), device)
    if device == "cuda":
        torch.cuda.synchronize()
    start = time.perf_counter()
    results = _run_device(torch, rows, specs, resamples_per_spec, device)
    if device == "cuda":
        torch.cuda.synchronize()
    return results, time.perf_counter() - start


def _run_device(
    torch: Any,
    rows: list[dict[str, float]],
    specs: list[dict[str, Any]],
    resamples_per_spec: int,
    device: str,
) -> list[float]:
    output: list[float] = []
    for spec_index, spec in enumerate(specs):
        filtered_rows = apply_filter(rows, str(spec["sample_filter"]))
        design, outcome = design_matrix(filtered_rows, spec)
        x_cpu = torch.tensor(design, dtype=torch.float64)
        y_cpu = torch.tensor(outcome, dtype=torch.float64)
        generator = torch.Generator(device="cpu").manual_seed(7000 + spec_index)
        indices = torch.randint(
            0,
            len(filtered_rows),
            (resamples_per_spec, len(filtered_rows)),
            generator=generator,
        )
        x = x_cpu[indices].to(device)
        y = y_cpu[indices].to(device)
        xt = x.transpose(1, 2)
        xtx = xt.matmul(x)
        ridge_lambda = 1e-6 if spec.get("estimator") == "ridge_1e-6" else 1e-8
        ridge = ridge_lambda * torch.eye(xtx.shape[-1], dtype=torch.float64, device=device).unsqueeze(0)
        xty = xt.matmul(y.unsqueeze(-1))
        beta = torch.linalg.solve(xtx + ridge, xty).squeeze(-1)
        output.extend(beta[:, 1].detach().cpu().tolist())
    return output
