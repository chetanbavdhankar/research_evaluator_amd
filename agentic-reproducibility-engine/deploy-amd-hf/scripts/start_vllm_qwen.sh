#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="${MODEL_ID:-Qwen/Qwen3.5-27B}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-qwen3.5-27b-amd}"
VLLM_HOST="${VLLM_HOST:-0.0.0.0}"
VLLM_PORT="${VLLM_PORT:-8000}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-1}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
DTYPE="${DTYPE:-auto}"
ENABLE_QWEN_TOOL_CALLING="${ENABLE_QWEN_TOOL_CALLING:-1}"

args=(
  serve "$MODEL_ID"
  --host "$VLLM_HOST"
  --port "$VLLM_PORT"
  --served-model-name "$SERVED_MODEL_NAME"
  --max-model-len "$MAX_MODEL_LEN"
  --tensor-parallel-size "$TENSOR_PARALLEL_SIZE"
  --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION"
  --dtype "$DTYPE"
  --language-model-only
)

if [ "$ENABLE_QWEN_TOOL_CALLING" = "1" ]; then
  args+=(
    --reasoning-parser qwen3
    --enable-auto-tool-choice
    --tool-call-parser qwen3_coder
  )
fi

echo "Starting vLLM model server"
echo "  model: $MODEL_ID"
echo "  served name: $SERVED_MODEL_NAME"
echo "  endpoint: http://$VLLM_HOST:$VLLM_PORT/v1"

exec vllm "${args[@]}"
