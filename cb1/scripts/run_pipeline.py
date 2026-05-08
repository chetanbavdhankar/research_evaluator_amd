from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the SpecCurve L0 deterministic pipeline.")
    parser.add_argument("--artifact-dir", default="artifacts", type=Path)
    parser.add_argument(
        "--source",
        choices=["demo", "rdatasets", "csv", "nber-dw", "nber-psid"],
        default="demo",
    )
    parser.add_argument("--csv-path", type=Path)
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--max-specs", type=int, default=240)
    args = parser.parse_args()

    result = run_pipeline(
        artifact_dir=args.artifact_dir,
        source=args.source,
        csv_path=args.csv_path,
        allow_network=args.allow_network,
        max_specs=args.max_specs,
    )
    print(f"artifact_dir={result['artifact_dir']}")
    print(f"dataset_hash={result['dataset_card']['dataset_hash']}")
    print(f"approved_specs={len(result['approved_specs'])}")
    print(f"rejected_specs={len(result['rejected_specs'])}")
    print(f"result_count={len(result['results'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
