from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.artifacts import read_json, write_json, write_text
from speccurve_l0.benchmark_contract import (
    benchmark_sha256_path,
    hardware_log_path,
    validate_benchmark_contract,
    validate_hardware_log_contract,
    write_benchmark_sha256,
)
from speccurve_l0.report import render_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import and validate a benchmark.json generated on AMD MI300X."
    )
    parser.add_argument("benchmark_json", type=Path)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument(
        "--hardware-log",
        type=Path,
        help="Path to methodology/hardware.log produced with benchmark.json.",
    )
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()

    source = args.benchmark_json
    artifact_dir = args.artifact_dir
    destination = artifact_dir / "benchmark.json"

    benchmark = read_json(source)
    dataset_card = read_json(artifact_dir / "dataset-card.json")
    failures = validate_benchmark_contract(
        benchmark,
        dataset_hash=str(dataset_card.get("dataset_hash")),
    )
    if failures:
        print("benchmark contract failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    source_hardware_log = _resolve_source_hardware_log(source, args.hardware_log)
    if source_hardware_log is None:
        print("benchmark contract failed:")
        print("- methodology/hardware.log is required with benchmark.json")
        return 1

    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == destination.resolve():
        write_json(destination, benchmark)
    else:
        shutil.copy2(source, destination)
        write_json(destination, benchmark)

    digest = write_benchmark_sha256(destination)
    destination_hardware_log = hardware_log_path(artifact_dir)
    destination_hardware_log.parent.mkdir(parents=True, exist_ok=True)
    if source_hardware_log.resolve() != destination_hardware_log.resolve():
        shutil.copy2(source_hardware_log, destination_hardware_log)
    hardware_log_failures = validate_hardware_log_contract(destination_hardware_log, benchmark)
    if hardware_log_failures:
        print("hardware log contract failed:")
        for failure in hardware_log_failures:
            print(f"- {failure}")
        return 1

    if not args.no_report:
        _render_report(artifact_dir, benchmark)

    print(f"imported {destination}")
    print(f"wrote {benchmark_sha256_path(destination)}")
    print(f"wrote {destination_hardware_log}")
    print(f"sha256={digest}")
    return 0


def _render_report(artifact_dir: Path, benchmark: dict) -> None:
    report = render_report(
        read_json(artifact_dir / "dataset-card.json"),
        read_json(artifact_dir / "robustness-surface.json"),
        read_json(artifact_dir / "specs-approved.json"),
        read_json(artifact_dir / "specs-rejected.json"),
        baseline=read_json(artifact_dir / "baseline.json"),
        benchmark=benchmark,
    )
    write_text(artifact_dir / "report.md", report)


def _resolve_source_hardware_log(source: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit if explicit.exists() else None
    candidates = [
        source.parent / "methodology" / "hardware.log",
        source.parent.parent / "methodology" / "hardware.log",
        source.with_name("hardware.log"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


if __name__ == "__main__":
    raise SystemExit(main())
