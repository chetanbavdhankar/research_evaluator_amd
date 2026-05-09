# Static Hugging Face Space Frontend

The frontend is the parent `index.html`. It is intentionally static HTML, not Gradio.

## Minimal Static Space

Create a new Hugging Face Space:

- SDK: Static
- Visibility: public or private
- Main file: `index.html`

Upload:

```text
agentic-reproducibility-engine/index.html
```

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

## Production Checklist

- Put HTTPS in front of the AMD backend.
- Keep the vLLM port private; expose only the agent API.
- Use a DNS name for the API host so the Space URL stays stable.
- Run `python deploy-amd-hf/scripts/check_amd_readiness.py --strict` after deploy.
- Capture one successful audit run and the `/health` payload for submission evidence.
