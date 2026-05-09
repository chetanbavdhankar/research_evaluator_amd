# Agentic Reproducibility Engine

AMD/Qwen multi-agent research reproducibility evaluator.

This folder is the runnable product surface for the agentic workflow submission. It contains a hostable static HTML frontend, a FastAPI backend, live evidence resolver tools, a multi-agent audit graph, and an eval harness that grades both agent contracts and final audit quality.

## What This Is

The system audits a research paper for reproducibility. It reads the paper, extracts claims and artifacts, resolves external evidence, scores reproducibility risk, plans follow-up experiments, checks its own assumptions, and emits an audit-ready report with provenance.

The intended production architecture is:

```text
Static HTML frontend on Hugging Face Space
        |
        v
FastAPI agent backend on AMD Developer Cloud
        |
        v
Multi-agent audit graph
        |
        v
OpenAI-compatible Qwen3.5-27B endpoint served by vLLM on ROCm
        |
        v
Tools: parser, arXiv resolver, DOI resolver, GitHub resolver,
dataset resolver, scorer, code/data planner, verifier, report writer
```

## Why It Is Different

- It is a working app, not a wiki or static writeup.
- The UI streams agent artifacts, tool calls, resolver outcomes, verifier objections, and final report provenance.
- Each audit stage gets its own prompt/context, model call, tool access boundary, and output artifact.
- The autonomy slider lets the user choose between local-only analysis, model-backed analysis, live evidence retrieval, and verifier repair behavior.
- The eval suite checks whether each agent performed its role and whether the overall audit decision is justified.

## Folder Contents

| Path | Purpose |
| --- | --- |
| `index.html` | Static hostable frontend. Can be served locally or uploaded to a static Hugging Face Space. |
| `app.py` | Local entrypoint that serves the API and frontend together. |
| `src/agentic_research_evaluator/` | Agent runtime, API, tools, schemas, reporting, model adapters, and eval logic. |
| `evals/agentic_audit_cases.json` | Golden audit cases for the deterministic eval harness. |
| `.claude/evals/agentic-reproducibility.md` | Eval definition and release gate. |
| `tests/` | Unit tests for the graph and eval harness. |
| `scripts/run_evals.py` | Offline and model-backed eval runner. |
| `scripts/vllm-qwen35-amd.sh` | AMD/vLLM launch script for Qwen/Qwen3.5-27B. |
| `deploy-amd-hf/` | Self-serve AMD GPU and Hugging Face deployment kit: runbook, env template, ROCm Docker/Compose scaffold, startup scripts, readiness checker, and static Space notes. |
| `DIFFERENTIATION.md` | Short explanation of why this product is distinct from the rest of the repo. |

## Local Quickstart

```powershell
cd agentic-reproducibility-engine
python -m venv .venv
.venv\Scripts\activate
pip install -e .[api,test]
python app.py
```

Open `http://127.0.0.1:8080`.

The app defaults to a deterministic local model runtime if no external model endpoint is configured. That keeps tests repeatable. Evidence resolution is still represented as explicit resolver results, and missing live evidence is recorded as a gap rather than fabricated.

## Run Tests And Evals

```powershell
pytest
python scripts/run_evals.py --k 1
python scripts/run_evals.py --k 3
```

Run the eval suite against the configured model runtime:

```powershell
python scripts/run_evals.py --runtime env --k 3
```

The eval harness checks:

- Planner artifact quality.
- Paper reading and claim extraction.
- Evidence resolver use and non-placeholder provenance.
- Reproducibility scoring.
- Experiment planning.
- Code/data planning.
- Verifier objections and decision degradation.
- Final report provenance and overall audit success.

## Local Gemini Smoke Test

Gemini is useful for validating the provider boundary before the AMD/Qwen endpoint is online. It is not the target submission model.

```powershell
$env:MODEL_PROVIDER="gemini"
$env:GEMINI_API_KEY="<your key>"
$env:GEMINI_MODEL="gemini-3-flash-preview"
python scripts/run_evals.py --runtime env --k 1
python app.py
```

## AMD/Qwen Runtime

For self-serve AMD GPU deployment, start with:

```text
deploy-amd-hf/README.md
deploy-amd-hf/DEPLOY_AMD.md
```

On the AMD instance, serve Qwen/Qwen3.5-27B with vLLM:

```bash
./scripts/vllm-qwen35-amd.sh
```

Then point the agent backend at the OpenAI-compatible vLLM endpoint:

```powershell
$env:MODEL_BASE_URL="http://127.0.0.1:8000/v1"
$env:MODEL_NAME="qwen3.5-27b-amd"
$env:MODEL_API_KEY="EMPTY"
python app.py
```

The launch script uses:

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

## Static Frontend Deployment

`index.html` is the public frontend. It does not require Gradio.

Deployment options:

- Same-origin: run `python app.py` and serve the frontend/API together.
- Static Hugging Face Space: upload `index.html` and pass the AMD API URL with `?api=https://<amd-api-host>`.
- Locked-down production API: set `CORS_ORIGINS=https://<space-name>.hf.space` on the backend.

## Submission Evidence To Capture

- AMD GPU name and ROCm version.
- vLLM startup log for Qwen/Qwen3.5-27B.
- Agent API `/health` payload.
- One successful audit run manifest with agent calls, tool calls, evidence count, model profile, and final report.
- Latency or tokens/sec from a Qwen-backed run.
- Eval output from `python scripts/run_evals.py --runtime env --k 3`.
