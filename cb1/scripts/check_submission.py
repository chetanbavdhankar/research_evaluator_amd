from __future__ import annotations

import argparse
import json
import re
import socket
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.artifacts import file_hash
from speccurve_l0.benchmark_contract import (
    benchmark_sha256_path,
    hardware_log_path,
    validate_benchmark_contract,
    validate_hardware_log_contract,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
DEFAULT_AMD_HOST = "165.245.141.127"
DEFAULT_AMD_PORT = 8000


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SpecCurve L0 submission readiness.")
    parser.add_argument("--amd-host", default=DEFAULT_AMD_HOST)
    parser.add_argument("--amd-port", type=int, default=DEFAULT_AMD_PORT)
    parser.add_argument("--skip-amd-socket", action="store_true")
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    checks.append(_check_file("README.md", ROOT / "README.md"))
    checks.append(_check_file("app.py", ROOT / "app.py"))
    checks.append(_check_file("requirements.txt", ROOT / "requirements.txt"))
    checks.append(_check_file("requirements-amd.txt", ROOT / "requirements-amd.txt"))
    checks.append(_check_file("cover.png", ROOT / "assets" / "cover.png"))
    checks.append(_check_file("demo-loop.gif", ROOT / "assets" / "demo-loop.gif"))
    checks.append(_check_file("slides.html", ROOT / "assets" / "slides.html"))
    checks.append(_check_file("demo-script", ROOT / "docs" / "DEMO_SCRIPT.md"))
    checks.append(_check_file("pitch-deck", ROOT / "docs" / "PITCH_DECK.md"))
    checks.append(_check_file("submission-packet", ROOT / "docs" / "SUBMISSION_PACKET.md"))
    checks.append(_check_file("build-in-public-drafts", ROOT / "docs" / "BUILD_IN_PUBLIC_DRAFTS.md"))
    checks.append(_check_file("amd-rocm-feedback", ROOT / "docs" / "AMD_ROCM_FEEDBACK.md"))
    checks.append(_check_file("submission-zip", ROOT / "dist" / "speccurve-l0-hf-space-submission.zip"))
    checks.append(_check_file("hf-space-export", ROOT / "dist" / "hf-space-export.zip"))
    checks.append(_check_file("hf-static-space-export", ROOT / "dist" / "hf-static-space-export.zip"))
    checks.append(_check_file("package-checksums", ROOT / "dist" / "checksums.sha256"))
    checks.append(_hf_space_export_check())
    checks.append(_static_space_export_check())
    checks.append(_demo_isolation_check())
    checks.append(_check_file("dataset-card.json", ARTIFACTS / "dataset-card.json"))
    checks.append(_check_file("baseline.json", ARTIFACTS / "baseline.json"))
    checks.append(_check_file("result-table.json", ARTIFACTS / "result-table.json"))
    checks.append(_check_file("robustness-surface.json", ARTIFACTS / "robustness-surface.json"))
    checks.append(_check_file("report.md", ARTIFACTS / "report.md"))
    checks.append(_check_file("surface.svg", ARTIFACTS / "surface.svg"))
    checks.extend(_artifact_contract_checks())
    checks.append(_copy_language_check())
    if args.skip_amd_socket:
        checks.append(
            {
                "check": "amd_backend_reachable",
                "status": "external_blocker",
                "detail": "Socket check skipped; live Space/backend URL still requires external proof.",
            }
        )
    else:
        checks.append(_socket_check(args.amd_host, args.amd_port))

    overall = _overall_status(checks)
    output = {"overall": overall, "checks": checks}
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if any(check["status"] == "fail" for check in checks) else 0


def _overall_status(checks: list[dict[str, Any]]) -> str:
    statuses = {str(check["status"]) for check in checks}
    if "fail" in statuses:
        return "fail"
    if "external_blocker" in statuses:
        return "ready_with_external_blocker"
    if "warn" in statuses:
        return "ready_with_warning"
    return "ready"


def _check_file(label: str, path: Path) -> dict[str, Any]:
    return {
        "check": f"file:{label}",
        "status": "pass" if path.exists() else "fail",
        "path": str(path),
    }


def _artifact_contract_checks() -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    try:
        dataset = _read_json(ARTIFACTS / "dataset-card.json")
        approved = _read_json(ARTIFACTS / "specs-approved.json")
        rejected = _read_json(ARTIFACTS / "specs-rejected.json")
        surface = _read_json(ARTIFACTS / "robustness-surface.json")
    except FileNotFoundError as exc:
        return [{"check": "artifact_contract", "status": "fail", "detail": str(exc)}]

    checks.append(
        {
            "check": "approved_specs_at_least_200",
            "status": "pass" if len(approved) >= 200 else "fail",
            "value": len(approved),
        }
    )
    checks.append(
        {
            "check": "invalid_fixture_rejections",
            "status": "pass" if len(rejected) >= 4 else "fail",
            "value": len(rejected),
        }
    )
    checks.append(
        {
            "check": "surface_raw_scale",
            "status": "pass" if surface.get("primary_transform") == "raw" else "fail",
            "value": surface.get("primary_transform"),
        }
    )
    estimators = {str(spec.get("estimator")) for spec in approved}
    required_estimators = {"ols", "ridge_1e-6", "psm_1nn", "ipw_att", "mahalanobis_1nn", "cem_att"}
    checks.append(
        {
            "check": "wiki_c_matching_weighting_estimators",
            "status": "pass" if required_estimators.issubset(estimators) else "fail",
            "value": sorted(estimators),
            "required": sorted(required_estimators),
        }
    )
    propensity_models = {str(spec.get("propensity_model", "none")) for spec in approved}
    checks.append(
        {
            "check": "propensity_model_dimensions",
            "status": "pass" if {"logit_l2", "probit_gradient"}.issubset(propensity_models) else "fail",
            "value": sorted(propensity_models),
        }
    )
    evidence_status = str(dataset.get("evidence_status"))
    if evidence_status.startswith("frozen_nber_source"):
        dataset_status = "pass"
        detail = "Frozen NBER source files are recorded in dataset-card.json."
    elif evidence_status == "demo_only_not_claim_evidence":
        dataset_status = "external_blocker"
        detail = "Demo fixture validates software behavior only; final data evidence must replace it."
    else:
        dataset_status = "warn"
        detail = "Dataset is not demo, but final source/citation status needs review."
    checks.append(
        {
            "check": "dataset_gate",
            "status": dataset_status,
            "value": dataset.get("evidence_status"),
            "detail": detail,
        }
    )
    checks.append(_benchmark_contract_check(dataset))
    return checks


def _benchmark_contract_check(dataset: dict[str, Any]) -> dict[str, Any]:
    benchmark_path = ARTIFACTS / "benchmark.json"
    if not benchmark_path.exists():
        return {
            "check": "mi300x_benchmark_artifact",
            "status": "external_blocker",
            "path": str(benchmark_path),
            "detail": "Generate this on AMD MI300X before final submission.",
        }

    benchmark = _read_json(benchmark_path)
    failures = validate_benchmark_contract(benchmark, dataset_hash=str(dataset.get("dataset_hash")))
    sha_path = benchmark_sha256_path(benchmark_path)
    if not sha_path.exists():
        failures.append("benchmark.json.sha256 is missing")
    else:
        expected = sha_path.read_text(encoding="utf-8").split()[0]
        actual = file_hash(benchmark_path)
        if expected != actual:
            failures.append("benchmark.json.sha256 does not match benchmark.json")
    log_path = hardware_log_path(ARTIFACTS)
    failures.extend(validate_hardware_log_contract(log_path, benchmark))

    return {
        "check": "mi300x_benchmark_contract",
        "status": "pass" if not failures else "fail",
        "path": str(benchmark_path),
        "sha256_path": str(sha_path),
        "hardware_log_path": str(log_path),
        "failures": failures,
    }


def _copy_language_check() -> dict[str, Any]:
    pattern = re.compile(
        r"replicated|replication crisis|\bproved\b|prove the paper|\bfraud\b|misconduct|"
        r"truth verdict|\bsolved\b",
        re.IGNORECASE,
    )
    findings: list[str] = []
    roots = [
        ROOT / "README.md",
        ROOT / "docs",
        ROOT / "speccurve_l0",
        ROOT / "app.py",
        ROOT / "space",
        ROOT / "dist" / "hf-static-space-export",
    ]
    for root in roots:
        if not root.exists():
            continue
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file() or path.suffix not in {".html", ".json", ".md", ".py", ".svg"}:
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if pattern.search(line):
                    findings.append(f"{path.relative_to(ROOT)}:{line_number}")
    return {
        "check": "public_copy_language_lint",
        "status": "pass" if not findings else "fail",
        "findings": findings,
    }


def _hf_space_export_check() -> dict[str, Any]:
    export_dir = ROOT / "dist" / "hf-space-export"
    required = [
        "README.md",
        "app.py",
        "requirements.txt",
        "artifacts/dataset-card.json",
        "artifacts/report.md",
        "assets/cover.png",
        "speccurve_l0/pipeline.py",
    ]
    missing = [relative for relative in required if not (export_dir / relative).exists()]
    metadata_ok = False
    readme = export_dir / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        metadata_ok = "sdk: gradio" in text and "app_file: app.py" in text
    return {
        "check": "hf_space_export_contract",
        "status": "pass" if not missing and metadata_ok else "fail",
        "missing": missing,
        "metadata_ok": metadata_ok,
    }


def _static_space_export_check() -> dict[str, Any]:
    export_dir = ROOT / "dist" / "hf-static-space-export"
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
    missing = [relative for relative in required if not (export_dir / relative).exists()]
    metadata_ok = False
    isolation_ok = False
    forbidden_hits: list[str] = []
    readme = export_dir / "README.md"
    index = export_dir / "index.html"
    status_path = export_dir / "data" / "status.json"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        metadata_ok = "sdk: static" in text and "app_file: index.html" in text
    if index.exists():
        text = index.read_text(encoding="utf-8")
        forbidden = ["innerHTML", "eval(", "new Function", "fetch('http", 'fetch("http']
        forbidden_hits = [token for token in forbidden if token in text]
    if status_path.exists():
        status = _read_json(status_path)
        isolation = status.get("execution_isolation", {})
        isolation_ok = (
            isolation.get("server_side_execution") is False
            and isolation.get("user_uploads") is False
            and isolation.get("backend_api_calls") is False
            and isolation.get("user_supplied_code") is False
        )
    benchmark_missing: list[str] = []
    if (export_dir / "data" / "benchmark.json").exists():
        benchmark_required = [
            "data/benchmark.json.sha256",
            "methodology/hardware.log",
        ]
        benchmark_missing = [
            relative for relative in benchmark_required if not (export_dir / relative).exists()
        ]
    return {
        "check": "hf_static_space_export_contract",
        "status": (
            "pass"
            if not missing and metadata_ok and isolation_ok and not forbidden_hits and not benchmark_missing
            else "fail"
        ),
        "missing": missing,
        "benchmark_missing": benchmark_missing,
        "metadata_ok": metadata_ok,
        "isolation_ok": isolation_ok,
        "forbidden_hits": forbidden_hits,
    }


def _demo_isolation_check() -> dict[str, Any]:
    app_text = (ROOT / "app.py").read_text(encoding="utf-8")
    isolated = "DEMO_ARTIFACT_DIR" in app_text and "run_pipeline(DEMO_ARTIFACT_DIR" in app_text
    return {
        "check": "demo_pipeline_isolated_from_evidence_artifacts",
        "status": "pass" if isolated else "fail",
        "detail": "Demo pipeline should not overwrite the frozen evidence artifact directory.",
    }


def _socket_check(host: str, port: int) -> dict[str, Any]:
    try:
        with socket.create_connection((host, port), timeout=4):
            return {
                "check": "amd_backend_reachable",
                "status": "pass",
                "host": host,
                "port": port,
            }
    except OSError as exc:
        return {
            "check": "amd_backend_reachable",
            "status": "external_blocker",
            "host": host,
            "port": port,
            "detail": str(exc),
        }


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
