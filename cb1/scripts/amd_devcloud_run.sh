#!/usr/bin/env bash
set -euo pipefail

RESAMPLES_PER_SPEC="${RESAMPLES_PER_SPEC:-256}"
SPEC_LIMIT="${SPEC_LIMIT:-64}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

cd "$(dirname "$0")/.."

python -m pip install --upgrade pip
python -m pip install -r requirements-amd.txt

if [[ "${SKIP_MI300X_PREFLIGHT:-0}" != "1" ]]; then
  python scripts/mi300x_preflight.py
fi

python scripts/run_pipeline.py --source nber-psid --allow-network --max-specs 240
python scripts/run_benchmark.py \
  --require-mi300x \
  --resamples-per-spec "${RESAMPLES_PER_SPEC}" \
  --spec-limit "${SPEC_LIMIT}"

python scripts/finalize_submission.py

if [[ "${START_BACKEND:-1}" == "1" ]]; then
  python scripts/start_amd_backend.py --host "${HOST}" --port "${PORT}"
fi
