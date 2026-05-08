from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.benchmark import detect_torch_hardware, run_benchmark
from speccurve_l0.artifacts import read_json, write_text
from speccurve_l0.pipeline import run_pipeline
from speccurve_l0.report import render_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the AMD MI300X benchmark contract.")
    parser.add_argument("--artifact-dir", default="artifacts", type=Path)
    parser.add_argument("--resamples-per-spec", type=int, default=64)
    parser.add_argument("--spec-limit", type=int, default=24)
    parser.add_argument("--require-mi300x", action="store_true", default=False)
    parser.add_argument("--detect-only", action="store_true")
    parser.add_argument(
        "--source",
        choices=["demo", "rdatasets", "csv", "nber-dw", "nber-psid"],
        default="demo",
    )
    parser.add_argument("--csv-path", type=Path)
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()

    if args.detect_only:
        print(f"hardware={detect_torch_hardware()}")
        return 0

    if not (args.artifact_dir / "dataset-card.json").exists():
        run_pipeline(
            artifact_dir=args.artifact_dir,
            source=args.source,
            csv_path=args.csv_path,
            allow_network=args.allow_network,
        )

    hardware = detect_torch_hardware()
    print(f"hardware={hardware}")
    benchmark = run_benchmark(
        artifact_dir=args.artifact_dir,
        resamples_per_spec=args.resamples_per_spec,
        spec_limit=args.spec_limit,
        require_mi300x=args.require_mi300x,
    )
    _render_report(args.artifact_dir, benchmark)
    print(f"benchmark_id={benchmark['benchmark_id']}")
    print(f"speedup={benchmark['speedup']}")
    print(f"submission_ready={benchmark['submission_ready']}")
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


if __name__ == "__main__":
    raise SystemExit(main())
