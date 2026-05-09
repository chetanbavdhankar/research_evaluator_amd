# Deploy On AMD GPU With Hugging Face Models

This runbook turns a fresh AMD GPU instance into a public agentic reproducibility evaluator.

The default target model is `Qwen/Qwen3.5-27B`, served by vLLM behind an OpenAI-compatible API. The app can also point to another Hugging Face model if vLLM can serve it with the same chat-completions contract.

## 1. Provision The Instance

Use an AMD GPU instance with ROCm support. For `Qwen/Qwen3.5-27B`, prefer a large-memory GPU such as MI300X. Smaller GPUs may need a smaller model, shorter context, or a quantized/runtime-specific configuration.

Expected host capabilities:

- Linux with ROCm installed and visible to user processes.
- `rocminfo` or `rocm-smi` available.
- Python compatible with the selected vLLM ROCm build.
- Enough disk for the Hugging Face model cache.
- Inbound access to the agent API port, typically `8080`.
- Inbound access to the vLLM port only if debugging remotely; keep `8000` private in production.

## 2. Clone The Repo

```bash
git clone https://github.com/chetanbavdhankar/research_evaluator_amd.git
cd research_evaluator_amd/agentic-reproducibility-engine
```

## 3. Configure Environment

```bash
cp deploy-amd-hf/.env.example .env
```

Edit `.env` for the host:

```bash
MODEL_ID=Qwen/Qwen3.5-27B
SERVED_MODEL_NAME=qwen3.5-27b-amd
MAX_MODEL_LEN=32768
MODEL_BASE_URL=http://127.0.0.1:8000/v1
MODEL_NAME=qwen3.5-27b-amd
CORS_ORIGINS=https://your-space-name.hf.space
```

If the model or download path needs authentication:

```bash
HF_TOKEN=hf_your_token
```

Do not commit `.env`.

## 4. Install App Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[api,test]"
pip install -r deploy-amd-hf/requirements-amd.txt
```

Install the ROCm-compatible vLLM build that matches your ROCm, Python, and GPU stack. The correct wheel or container varies by host image, so treat vLLM installation as the host-specific step and verify it with:

```bash
python -m vllm.entrypoints.openai.api_server --help >/dev/null
vllm --help >/dev/null
```

## 5. Run Readiness Check

Before starting services:

```bash
python deploy-amd-hf/scripts/check_amd_readiness.py
```

After services are running:

```bash
python deploy-amd-hf/scripts/check_amd_readiness.py --strict
```

The strict mode requires the vLLM `/models` endpoint and the agent `/health` endpoint to be reachable.

## 6. Start vLLM

```bash
set -a
source .env
set +a

deploy-amd-hf/scripts/start_vllm_qwen.sh
```

The script starts:

```bash
vllm serve Qwen/Qwen3.5-27B \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name qwen3.5-27b-amd \
  --max-model-len 32768 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --language-model-only
```

Override defaults through `.env` when needed:

```bash
MODEL_ID=Qwen/Qwen3.5-27B
MAX_MODEL_LEN=32768
TENSOR_PARALLEL_SIZE=1
GPU_MEMORY_UTILIZATION=0.90
```

## 7. Start Agent API And Frontend

In a second shell:

```bash
set -a
source .env
set +a

deploy-amd-hf/scripts/start_agent_api.sh
```

Check:

```bash
curl http://127.0.0.1:8080/health
```

Open:

```text
http://<amd-host>:8080
```

The FastAPI app serves the static `index.html` at `/` and streams audit events from `/runs/stream`.

## 8. Run Product Evals On The Host

```bash
python scripts/run_evals.py --runtime env --k 1
python scripts/run_evals.py --runtime env --k 3
```

Record:

- `pass@k` and `pass^k`.
- `/health` response.
- vLLM startup log.
- One completed audit run ID.
- GPU name and ROCm version from the readiness check.

## 9. Optional Docker Compose Path

From `agentic-reproducibility-engine/`:

```bash
cp deploy-amd-hf/.env.example .env
docker compose -f deploy-amd-hf/docker-compose.amd.yml up --build
```

The compose file exposes:

- vLLM: `http://127.0.0.1:8000/v1`
- Agent UI/API: `http://127.0.0.1:8080`

The Dockerfile leaves the exact vLLM ROCm install command configurable because the correct package depends on the host ROCm/Python matrix.

## 10. Static Hugging Face Space

For a public static Space, use:

```text
agentic-reproducibility-engine/index.html
```

Configure the Space URL to point at the AMD backend:

```text
https://your-space-name.hf.space/?api=https://your-amd-api-host
```

Set the backend CORS:

```bash
CORS_ORIGINS=https://your-space-name.hf.space
```

More details are in `huggingface-space/README.md`.

## Production Notes

- Put TLS in front of the FastAPI host before sharing broadly.
- Do not expose vLLM directly unless it is behind an authenticated network boundary.
- Keep `RUN_STORE_DIR` on persistent disk if audit records need to survive restarts.
- Use `MAX_MODEL_LEN=32768` first, then increase only after observing memory headroom.
- Use a smaller Hugging Face model if the GPU cannot load `Qwen/Qwen3.5-27B`.
