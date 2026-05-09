#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

export MODEL_BASE_URL="${MODEL_BASE_URL:-http://127.0.0.1:${VLLM_PORT:-8000}/v1}"
export MODEL_NAME="${MODEL_NAME:-${SERVED_MODEL_NAME:-qwen3.5-27b-amd}}"
export MODEL_API_KEY="${MODEL_API_KEY:-EMPTY}"
export CORS_ORIGINS="${CORS_ORIGINS:-*}"
export RUN_STORE_DIR="${RUN_STORE_DIR:-runs}"

AGENT_HOST="${AGENT_HOST:-0.0.0.0}"
AGENT_PORT="${AGENT_PORT:-8080}"

echo "Starting Agentic Reproducibility Engine API"
echo "  API: http://$AGENT_HOST:$AGENT_PORT"
echo "  model endpoint: $MODEL_BASE_URL"
echo "  model name: $MODEL_NAME"

exec python -m uvicorn agentic_research_evaluator.api:app --host "$AGENT_HOST" --port "$AGENT_PORT"
