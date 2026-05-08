from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the local finalization checks and rebuild submission bundles."
    )
    parser.add_argument("--check-amd-socket", action="store_true")
    args = parser.parse_args()

    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        [sys.executable, "-m", "compileall", "-q", "app.py", "speccurve_l0", "scripts", "tests"],
        [sys.executable, "scripts/create_submission_assets.py"],
        [sys.executable, "scripts/export_hf_space.py"],
        [sys.executable, "scripts/export_static_space.py"],
        [sys.executable, "scripts/package_submission.py"],
        [sys.executable, "scripts/write_package_checksums.py"],
        [sys.executable, "scripts/check_submission.py"],
    ]
    if not args.check_amd_socket:
        commands[-1].append("--skip-amd-socket")

    for command in commands:
        print(f"running: {' '.join(command)}")
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode

    print("local finalization complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
