---
title: Agentic Reproducibility Engine
sdk: static
app_file: index.html
fullWidth: true
license: apache-2.0
---

# Agentic Reproducibility Engine

Static Hugging Face Space frontend for the AMD-hosted multi-agent reproducibility evaluator.
It is intentionally plain HTML, not Gradio, so the public app stays lightweight while the
agent API and Qwen/Qwen3.5-27B vLLM endpoint run on the AMD GPU instance.

## Files

```text
README.md   Space metadata and setup notes
index.html  Static frontend copied from the product root
```

## Runtime Shape

```text
Hugging Face Static Space
        |
        v
HTTPS Agent API on AMD Developer Cloud
        |
        v
Qwen/Qwen3.5-27B through vLLM on ROCm
```

The Space itself does not run the model. It calls the AMD-hosted backend.

## Connect To The AMD Backend

Open the Space with an API override:

```text
https://your-space-name.hf.space/?api=https://your-amd-api-host
```

The frontend calls:

```text
GET  /health
POST /runs
POST /runs/stream
GET  /runs/{run_id}
GET  /runs/{run_id}/report
```

The AMD backend must allow the Space origin:

```bash
CORS_ORIGINS=https://your-space-name.hf.space
```

For local testing, the backend can use:

```bash
CORS_ORIGINS=*
```

## Create With The Hugging Face CLI

After logging in with a write token:

```text
hf auth login
hf repo create lablab-ai-amd-developer-hackathon/agentic-reproducibility-engine --type space --space-sdk static
git clone https://huggingface.co/spaces/lablab-ai-amd-developer-hackathon/agentic-reproducibility-engine
copy README.md agentic-reproducibility-engine/README.md
copy index.html agentic-reproducibility-engine/index.html
cd agentic-reproducibility-engine
git add README.md index.html
git commit -m "Deploy static agentic reproducibility frontend"
git push
```

## Create With The Repo Script

From the product root:

```powershell
pip install -r deploy-amd-hf\requirements-amd.txt
$env:HF_TOKEN="hf_..."
python deploy-amd-hf\scripts\create_hf_static_space.py
```

## Create With `huggingface_hub`

The same operation can be automated with:

```python
from huggingface_hub import HfApi

api = HfApi(token="hf_...")
api.create_repo(
    repo_id="lablab-ai-amd-developer-hackathon/agentic-reproducibility-engine",
    repo_type="space",
    space_sdk="static",
    private=False,
    exist_ok=True,
)
api.upload_folder(
    folder_path="agentic-reproducibility-engine/deploy-amd-hf/huggingface-space",
    repo_id="lablab-ai-amd-developer-hackathon/agentic-reproducibility-engine",
    repo_type="space",
)
```

## Production Checklist

- Put HTTPS in front of the AMD backend.
- Keep the vLLM port private; expose only the agent API.
- Set `MODEL_ID=Qwen/Qwen3.5-27B` on the AMD instance.
- Set `SERVED_MODEL_NAME=qwen3.5-27b-amd` and match `MODEL_NAME` in the agent API.
- Use a DNS name for the API host so the Space URL stays stable.
- Run `python deploy-amd-hf/scripts/check_amd_readiness.py --strict` after deploy.
- Capture one successful audit run and the `/health` payload for submission evidence.
