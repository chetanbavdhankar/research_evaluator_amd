from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.benchmark import detect_torch_hardware


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that PyTorch can see AMD MI300X/ROCm.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON only.")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip the tensor smoke test.")
    args = parser.parse_args()

    hardware = detect_torch_hardware()
    smoke = {"skipped": True} if args.skip_smoke else _torch_gpu_smoke()
    rocm_smi = _rocm_smi_status()
    failures = evaluate_preflight(hardware, smoke)
    result = {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "hardware": hardware,
        "torch_gpu_smoke": smoke,
        "rocm_smi": rocm_smi,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_human(result)
    return 1 if failures else 0


def evaluate_preflight(hardware: dict[str, Any], smoke: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if hardware.get("torch_available") is not True:
        failures.append("PyTorch is not importable")
    if not hardware.get("gpu"):
        failures.append("PyTorch does not report a GPU device")
    if not hardware.get("hip"):
        failures.append("torch.version.hip is missing; this is not a ROCm/HIP PyTorch build")
    if hardware.get("is_mi300x") is not True:
        failures.append("GPU name does not identify an AMD MI300-class device")
    if smoke.get("skipped") is not True and smoke.get("status") != "pass":
        failures.append(f"GPU tensor smoke failed: {smoke.get('detail', 'unknown error')}")
    return failures


def _torch_gpu_smoke() -> dict[str, Any]:
    try:
        import torch
    except ImportError as exc:
        return {"status": "fail", "detail": f"PyTorch import failed: {exc}"}
    if not torch.cuda.is_available():
        return {"status": "fail", "detail": "torch.cuda.is_available() is false"}
    try:
        device = torch.device("cuda")
        x = torch.eye(128, dtype=torch.float64, device=device)
        y = x.matmul(x).sum()
        torch.cuda.synchronize()
        return {"status": "pass", "device": str(device), "sum": float(y.detach().cpu())}
    except Exception as exc:  # pragma: no cover - exercised only on GPU hosts.
        return {"status": "fail", "detail": repr(exc)}


def _rocm_smi_status() -> dict[str, Any]:
    executable = shutil.which("rocm-smi")
    if executable is None:
        return {"available": False, "reason": "not_found_on_path"}
    try:
        completed = subprocess.run(
            [executable, "--showproductname"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "command": executable, "error": repr(exc)}
    return {
        "available": True,
        "command": executable,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _print_human(result: dict[str, Any]) -> None:
    print(f"preflight_status={result['status']}")
    print("hardware=" + json.dumps(result["hardware"], sort_keys=True))
    print("torch_gpu_smoke=" + json.dumps(result["torch_gpu_smoke"], sort_keys=True))
    print("rocm_smi=" + json.dumps(result["rocm_smi"], sort_keys=True))
    if result["failures"]:
        print("failures:")
        for failure in result["failures"]:
            print(f"- {failure}")


if __name__ == "__main__":
    raise SystemExit(main())
