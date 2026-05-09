#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="${MODEL_ID:-Qwen/Qwen3.5-27B}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-qwen3.5-27b-amd}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"
PORT="${PORT:-8000}"

vllm serve "$MODEL_ID" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --served-model-name "$SERVED_MODEL_NAME" \
  --max-model-len "$MAX_MODEL_LEN" \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --language-model-only

