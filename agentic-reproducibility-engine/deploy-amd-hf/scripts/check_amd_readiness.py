#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    hint: str = ""
    required: bool = True


def run_command(command: list[str], timeout: int = 10) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output[:2000]


def http_json(url: str, timeout: int = 10) -> tuple[bool, str]:
    request = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        return False, str(exc)
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return False, body[:500]
    return True, json.dumps(parsed, indent=2)[:2000]


def rocm_version() -> str:
    candidates = [
        Path("/opt/rocm/.info/version"),
        Path("/opt/rocm/.info/version-dev"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8", errors="ignore").strip()
    ok, output = run_command(["rocminfo"], timeout=15)
    if ok:
        for line in output.splitlines():
            if "ROCm" in line or "Runtime Version" in line:
                return line.strip()
    return "not detected"


def gpu_summary() -> str:
    if shutil.which("rocm-smi"):
        ok, output = run_command(["rocm-smi", "--showproductname"], timeout=15)
        if ok and output:
            return output
    if shutil.which("rocminfo"):
        ok, output = run_command(["rocminfo"], timeout=15)
        if ok:
            useful = [
                line.strip()
                for line in output.splitlines()
                if "Marketing Name" in line or "Name:" in line or "gfx" in line
            ]
            return "\n".join(useful[:20]) or "rocminfo succeeded"
    return "no ROCm GPU command available"


def build_checks(strict: bool) -> list[Check]:
    checks: list[Check] = []

    python_ok = sys.version_info >= (3, 11)
    checks.append(
        Check(
            "python",
            python_ok,
            sys.version.replace("\n", " "),
            "Use Python 3.11+ for the agent API. Match vLLM's ROCm wheel requirements for the model server.",
        )
    )

    project_root = Path(__file__).resolve().parents[2]
    checks.append(
        Check(
            "project files",
            (project_root / "index.html").exists() and (project_root / "src").exists(),
            str(project_root),
            "Run this script from the checked-out agentic-reproducibility-engine folder.",
        )
    )

    rocm_tools = [tool for tool in ("rocminfo", "rocm-smi") if shutil.which(tool)]
    checks.append(
        Check(
            "rocm tools",
            bool(rocm_tools),
            ", ".join(rocm_tools) if rocm_tools else "not found",
            "Install ROCm on the AMD GPU host and ensure commands are on PATH.",
        )
    )

    checks.append(
        Check(
            "rocm version",
            rocm_version() != "not detected",
            rocm_version(),
            "ROCm version is used to select the matching vLLM build.",
            required=False,
        )
    )

    gpu_info = gpu_summary()
    checks.append(
        Check(
            "amd gpu",
            "no ROCm GPU command available" not in gpu_info,
            gpu_info,
            "Verify the instance exposes /dev/kfd and /dev/dri and the user can access them.",
        )
    )

    vllm_path = shutil.which("vllm")
    checks.append(
        Check(
            "vllm command",
            bool(vllm_path),
            vllm_path or "not found",
            "Install a ROCm-compatible vLLM build for this host.",
            required=strict,
        )
    )

    hf_token = os.environ.get("HF_TOKEN", "")
    checks.append(
        Check(
            "hugging face token",
            bool(hf_token),
            "set" if hf_token else "not set",
            "Public models may work without a token, but a token helps with rate limits and gated models.",
            required=False,
        )
    )

    model_base = os.environ.get("MODEL_BASE_URL", "http://127.0.0.1:8000/v1").rstrip("/")
    ok, detail = http_json(f"{model_base}/models", timeout=10)
    checks.append(
        Check(
            "vllm /models endpoint",
            ok,
            detail,
            "Start deploy-amd-hf/scripts/start_vllm_qwen.sh or update MODEL_BASE_URL.",
            required=strict,
        )
    )

    agent_base = os.environ.get("AGENT_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
    ok, detail = http_json(f"{agent_base}/health", timeout=10)
    checks.append(
        Check(
            "agent /health endpoint",
            ok,
            detail,
            "Start deploy-amd-hf/scripts/start_agent_api.sh or update AGENT_BASE_URL.",
            required=strict,
        )
    )

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Check AMD/HF deployment readiness.")
    parser.add_argument("--strict", action="store_true", help="Require running vLLM and agent endpoints.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    checks = build_checks(strict=args.strict)
    failed = [check for check in checks if check.required and not check.ok]

    if args.json:
        print(json.dumps({"ok": not failed, "checks": [asdict(check) for check in checks]}, indent=2))
        return 0 if not failed else 1

    print("AMD/Hugging Face readiness check")
    print("=" * 38)
    for check in checks:
        status = "PASS" if check.ok else ("FAIL" if check.required else "WARN")
        print(f"[{status}] {check.name}: {check.detail}")
        if not check.ok and check.hint:
            print(f"       hint: {check.hint}")

    print()
    print("Status:", "PASS" if not failed else "FAIL")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
