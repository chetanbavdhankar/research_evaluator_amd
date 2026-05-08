from __future__ import annotations

from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from speccurve_l0.artifacts import file_hash, write_text

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = DIST / "checksums.sha256"


def main() -> int:
    targets = [
        DIST / "hf-static-space-export.zip",
        DIST / "hf-space-export.zip",
        DIST / "speccurve-l0-hf-space-submission.zip",
    ]
    missing = [path.name for path in targets if not path.exists()]
    if missing:
        raise RuntimeError("missing package files: " + ", ".join(missing))
    lines = [f"{file_hash(path)}  {path.name}" for path in targets]
    write_text(OUTPUT, "\n".join(lines) + "\n")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
