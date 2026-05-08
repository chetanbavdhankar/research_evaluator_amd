from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "dist" / "hf-space-export"
EXPORT_ZIP = ROOT / "dist" / "hf-space-export.zip"

INCLUDE_PATHS = [
    "README.md",
    "app.py",
    "requirements.txt",
    ".env.example",
    "assets",
    "artifacts",
    "docs",
    "scripts",
    "speccurve_l0",
    "tests",
    "pyproject.toml",
    "requirements-amd.txt",
]
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache"}
EXCLUDED_FILES = {
    "gradio.err",
    "gradio.out",
    "server.err",
    "server.out",
    "server-job.log",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def main() -> int:
    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    EXPORT_DIR.mkdir(parents=True)

    for relative in INCLUDE_PATHS:
        source = ROOT / relative
        destination = EXPORT_DIR / relative
        if source.is_dir():
            _copy_dir(source, destination)
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    if EXPORT_ZIP.exists():
        EXPORT_ZIP.unlink()
    shutil.make_archive(str(EXPORT_ZIP.with_suffix("")), "zip", EXPORT_DIR)
    _validate_export(EXPORT_DIR)
    print(f"wrote {EXPORT_DIR}")
    print(f"wrote {EXPORT_ZIP}")
    return 0


def _copy_dir(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        if not path.is_file() or not _include(path):
            continue
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def _include(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.name in EXCLUDED_FILES:
        return False
    if path.name.startswith("server-") and path.suffix in {".out", ".err", ".log"}:
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def _validate_export(path: Path) -> None:
    required = [
        "README.md",
        "app.py",
        "requirements.txt",
        "artifacts/dataset-card.json",
        "artifacts/report.md",
        "artifacts/result-table.json",
        "artifacts/robustness-surface.json",
        "assets/cover.png",
        "assets/demo-loop.gif",
        "speccurve_l0/pipeline.py",
    ]
    missing = [relative for relative in required if not (path / relative).exists()]
    if missing:
        raise RuntimeError(f"HF export missing files: {', '.join(missing)}")
    readme = (path / "README.md").read_text(encoding="utf-8")
    if "sdk: gradio" not in readme or "app_file: app.py" not in readme:
        raise RuntimeError("README.md is missing Hugging Face Gradio metadata")


if __name__ == "__main__":
    raise SystemExit(main())
