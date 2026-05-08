from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist" / "speccurve-l0-hf-space-submission.zip"

EXCLUDED_DIRS = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".chrome-profile",
    "artifacts-demo",
    "dist",
}
EXCLUDED_FILES = {
    "gradio-running.png",
    "preview.png",
    "gradio.err",
    "gradio.out",
    "server.err",
    "server.out",
    "server-job.log",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()

    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and _include(path))
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())

    print(f"wrote {OUTPUT}")
    print(f"file_count={len(files)}")
    print(f"bytes={OUTPUT.stat().st_size}")
    return 0


def _include(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.name in EXCLUDED_FILES:
        return False
    if path.name.startswith("server-") and path.suffix in {".out", ".err", ".log"}:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
