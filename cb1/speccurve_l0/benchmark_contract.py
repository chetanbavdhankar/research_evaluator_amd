from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .artifacts import file_hash, stable_json, utc_now, write_text


def benchmark_sha256_path(benchmark_path: Path) -> Path:
    return benchmark_path.with_name(f"{benchmark_path.name}.sha256")


def hardware_log_path(artifact_dir: Path) -> Path:
    return artifact_dir / "methodology" / "hardware.log"


def write_benchmark_sha256(benchmark_path: Path) -> str:
    digest = file_hash(benchmark_path)
    write_text(benchmark_sha256_path(benchmark_path), f"{digest}  {benchmark_path.name}\n")
    return digest


def write_hardware_log(
    artifact_dir: Path,
    benchmark: dict[str, Any],
    detected_hardware: dict[str, Any],
    benchmark_path: Path | None = None,
    rocm_smi_command: str = "rocm-smi",
) -> Path:
    path = hardware_log_path(artifact_dir)
    digest = file_hash(benchmark_path) if benchmark_path is not None and benchmark_path.exists() else None
    runtime_summary = {
        "cpu_runtime_seconds": benchmark.get("cpu_runtime_seconds"),
        "gpu_runtime_seconds": benchmark.get("gpu_runtime_seconds"),
        "speedup": benchmark.get("speedup"),
        "throughput_cpu": benchmark.get("throughput_cpu"),
        "throughput_gpu": benchmark.get("throughput_gpu"),
        "tolerance_check": benchmark.get("tolerance_check"),
        "submission_ready": benchmark.get("submission_ready"),
    }
    sections = [
        "SpecCurve L0 AMD hardware evidence log",
        f"generated_at: {utc_now()}",
        f"benchmark_id: {benchmark.get('benchmark_id')}",
        f"benchmark_generated_at: {benchmark.get('generated_at')}",
        f"benchmark_file_sha256: {digest or 'not_available'}",
        f"dataset_hash: {benchmark.get('dataset_hash')}",
        f"spec_batch_id: {benchmark.get('spec_batch_id')}",
        "",
        "benchmark_hardware_json:",
        stable_json(benchmark.get("hardware", {})),
        "",
        "detected_hardware_json:",
        stable_json(detected_hardware),
        "",
        "benchmark_runtime_summary_json:",
        stable_json(runtime_summary),
        "",
        "rocm_smi_json:",
        stable_json(_capture_rocm_smi(rocm_smi_command)),
        "",
    ]
    write_text(path, "\n".join(sections))
    return path


def validate_hardware_log_contract(log_path: Path, benchmark: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if not log_path.exists():
        return ["methodology/hardware.log is missing"]

    text = log_path.read_text(encoding="utf-8", errors="replace")
    if len(text.strip()) < 200:
        failures.append("methodology/hardware.log is too small to be useful evidence")

    required_literals = [
        "SpecCurve L0 AMD hardware evidence log",
        "benchmark_hardware_json:",
        "detected_hardware_json:",
        "benchmark_runtime_summary_json:",
        "rocm_smi_json:",
    ]
    for literal in required_literals:
        if literal not in text:
            failures.append(f"methodology/hardware.log missing section: {literal}")

    for field in ("benchmark_id", "dataset_hash", "spec_batch_id", "generated_at"):
        value = benchmark.get(field)
        if value and str(value) not in text:
            failures.append(f"methodology/hardware.log does not reference {field}")

    gpu = benchmark.get("hardware", {}).get("gpu") if isinstance(benchmark.get("hardware"), dict) else None
    if gpu and str(gpu) not in text:
        failures.append("methodology/hardware.log does not include hardware.gpu")

    return failures


def validate_benchmark_contract(
    benchmark: dict[str, Any],
    dataset_hash: str | None = None,
) -> list[str]:
    failures: list[str] = []
    required = {
        "benchmark_id",
        "dataset_hash",
        "spec_batch_id",
        "approved_spec_count",
        "resamples_per_spec",
        "total_statistical_runs",
        "cpu_runtime_seconds",
        "gpu_runtime_seconds",
        "speedup",
        "throughput_cpu",
        "throughput_gpu",
        "tolerance_check",
        "warmup_policy",
        "hardware",
        "generated_at",
    }
    missing = sorted(required.difference(benchmark))
    if missing:
        failures.append(f"missing required fields: {', '.join(missing)}")

    if dataset_hash is not None and benchmark.get("dataset_hash") != dataset_hash:
        failures.append("benchmark dataset_hash does not match dataset-card.json")

    tolerance_check = benchmark.get("tolerance_check")
    if not isinstance(tolerance_check, str) or tolerance_check not in {"pass", "fail"}:
        failures.append("tolerance_check must be the Wiki C string value 'pass' or 'fail'")
    elif tolerance_check != "pass":
        failures.append("tolerance_check is not pass")

    hardware = benchmark.get("hardware")
    if not isinstance(hardware, dict):
        failures.append("hardware must be an object")
        hardware = {}

    if "MI300" not in str(hardware.get("gpu", "")).upper():
        failures.append("hardware.gpu does not identify an MI300-class device")
    if not hardware.get("hip"):
        failures.append("hardware.hip is missing")

    try:
        approved_spec_count = int(benchmark.get("approved_spec_count", 0))
        resamples_per_spec = int(benchmark.get("resamples_per_spec", 0))
        total_statistical_runs = int(benchmark.get("total_statistical_runs", 0))
    except (TypeError, ValueError):
        failures.append("approved_spec_count, resamples_per_spec, and total_statistical_runs must be integers")
    else:
        expected_runs = approved_spec_count * resamples_per_spec
        if total_statistical_runs != expected_runs:
            failures.append("total_statistical_runs does not equal approved_spec_count * resamples_per_spec")

    try:
        cpu_runtime = float(benchmark.get("cpu_runtime_seconds", 0))
        gpu_runtime = float(benchmark.get("gpu_runtime_seconds", 0))
        speedup = float(benchmark.get("speedup", 0))
    except (TypeError, ValueError):
        failures.append("cpu_runtime_seconds, gpu_runtime_seconds, and speedup must be numeric")
    else:
        if cpu_runtime <= 0:
            failures.append("cpu_runtime_seconds must be positive")
        if gpu_runtime <= 0:
            failures.append("gpu_runtime_seconds must be positive")
        if gpu_runtime > 0 and abs((cpu_runtime / gpu_runtime) - speedup) > 1e-6:
            failures.append("speedup does not match cpu_runtime_seconds / gpu_runtime_seconds")

    if benchmark.get("submission_ready") is not True:
        failures.append("submission_ready is not true")

    return failures


def _capture_rocm_smi(command: str) -> dict[str, Any]:
    executable = shutil.which(command)
    if executable is None:
        return {
            "available": False,
            "command": command,
            "reason": "not_found_on_path",
        }
    try:
        completed = subprocess.run(
            [executable],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "available": False,
            "command": executable,
            "error": repr(exc),
        }
    return {
        "available": True,
        "command": executable,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
