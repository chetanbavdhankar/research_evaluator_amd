# AMD GPU + Hugging Face Deployment Kit

This folder is the self-serve deployment path for running the Agentic Reproducibility Engine on an AMD GPU instance with Hugging Face models.

Use it when the target runtime is:

```text
Hugging Face static frontend
        |
        v
FastAPI agent backend on AMD GPU host
        |
        v
vLLM serving a Hugging Face model through an OpenAI-compatible API
```

## Files

| File | Purpose |
| --- | --- |
| `DEPLOY_AMD.md` | End-to-end AMD GPU deployment runbook. |
| `.env.example` | Environment variables for vLLM, the agent API, CORS, and Hugging Face model access. |
| `requirements-amd.txt` | Extra Python utilities useful on the AMD host. App dependencies still come from the parent `pyproject.toml`. |
| `Dockerfile.rocm` | ROCm-oriented container scaffold for the agent API and optional vLLM install. |
| `docker-compose.amd.yml` | Two-service local deployment: vLLM model server plus agent API/frontend server. |
| `scripts/start_vllm_qwen.sh` | Starts vLLM with Qwen/Qwen3.5-27B defaults. |
| `scripts/start_agent_api.sh` | Starts the FastAPI backend and serves `index.html`. |
| `scripts/check_amd_readiness.py` | No-dependency readiness checker for Python, ROCm, vLLM, model endpoint, and agent endpoint. |
| `huggingface-space/README.md` | Static Hugging Face Space deployment notes. |

## Fast Path

From `agentic-reproducibility-engine/`:

```bash
cp deploy-amd-hf/.env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[api,test]"
pip install -r deploy-amd-hf/requirements-amd.txt
python deploy-amd-hf/scripts/check_amd_readiness.py
```

Install a ROCm-compatible vLLM build for the host, then run:

```bash
set -a
source .env
set +a

deploy-amd-hf/scripts/start_vllm_qwen.sh
```

In a second shell:

```bash
set -a
source .env
set +a

deploy-amd-hf/scripts/start_agent_api.sh
```

Open `http://<amd-host>:8080`.

## Why This Is Separate

The parent app remains easy to run locally with a deterministic mock runtime. This folder is specifically for real AMD GPU deployment, Hugging Face model loading, vLLM serving, CORS, frontend hosting, and readiness checks.
