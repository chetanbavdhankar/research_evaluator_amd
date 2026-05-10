from __future__ import annotations

import argparse
import os
from pathlib import Path


DEFAULT_REPO_ID = "lablab-ai-amd-developer-hackathon/agentic-reproducibility-engine"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update the static Hugging Face Space frontend."
    )
    parser.add_argument(
        "--repo-id",
        default=DEFAULT_REPO_ID,
        help="Space repo id, for example org-or-user/space-name.",
    )
    parser.add_argument(
        "--folder",
        default=str(Path(__file__).resolve().parents[1] / "huggingface-space"),
        help="Local folder containing README.md and index.html.",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create the Space as private. Existing repos keep their current visibility.",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("HF_TOKEN"),
        help="Hugging Face write token. Defaults to HF_TOKEN.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.token:
        raise SystemExit("Missing Hugging Face token. Set HF_TOKEN or pass --token.")

    folder = Path(args.folder).resolve()
    readme = folder / "README.md"
    index = folder / "index.html"
    if not readme.exists() or not index.exists():
        raise SystemExit(f"Expected README.md and index.html in {folder}")

    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise SystemExit(
            "Missing huggingface_hub. Install with: pip install -r deploy-amd-hf/requirements-amd.txt"
        ) from exc

    api = HfApi(token=args.token)
    url = api.create_repo(
        repo_id=args.repo_id,
        repo_type="space",
        space_sdk="static",
        private=args.private,
        exist_ok=True,
    )
    commit = api.upload_folder(
        folder_path=str(folder),
        repo_id=args.repo_id,
        repo_type="space",
        commit_message="Deploy static agentic reproducibility frontend",
    )

    print(f"Space repo: {url}")
    print(f"Commit: {commit.oid}")
    print(f"App URL: https://{args.repo_id.replace('/', '-')}.hf.space")


if __name__ == "__main__":
    main()
