# Demo Runbook

Use this to record the video and to rehearse the live judging walkthrough.

## Pre-Demo Setup

1. Deploy the static frontend to a Hugging Face Space.
2. Deploy the backend on AMD Developer Cloud.
3. Start vLLM with `Qwen/Qwen3.5-27B`.
4. Start the FastAPI agent backend.
5. Open the Space with:

```text
https://<space-name>.hf.space/?api=https://<amd-backend-host>
```

6. Confirm `/health` shows the model endpoint is reachable.

## Paper To Use

Use a paper with clear external artifacts:

```text
Denoising Diffusion Probabilistic Models
arXiv: 2006.11239
DOI: 10.48550/arXiv.2006.11239
GitHub: hojonathanho/diffusion
Datasets: CIFAR-10, LSUN, CelebA-HQ
```

Alternative:

```text
Learning Transferable Visual Models From Natural Language Supervision
arXiv: 2103.00020
DOI: 10.48550/arXiv.2103.00020
GitHub: openai/CLIP
Datasets: WIT, ImageNet, Flickr30k
```

## Walkthrough

### 1. Show Product Entry

Open the dashboard and point out:

- Static frontend.
- Agent API health.
- Autonomy slider.
- Run audit and stop audit controls.
- Live trace area.

### 2. Start A New Audit

- Paste the paper metadata.
- Set autonomy to `L3` for the most complete agentic behavior.
- Start the audit.

### 3. Narrate The Live Trace

Call out:

- Planning artifact.
- Paper understanding artifact.
- Tool request validation.
- arXiv resolver.
- DOI resolver.
- GitHub resolver.
- Dataset resolver.
- Reproducibility score.
- Experiment plan.
- Code/data follow-up.
- Verifier objection.
- Final report.

### 4. Show Fail-Closed Behavior

If a resolver fails or evidence is missing, emphasize:

```text
The system records the gap and degrades the decision instead of inventing evidence.
```

### 5. Show Final Report

Open the report panel and show:

- Score.
- Decision.
- Evidence records.
- Gaps.
- Replication plan.
- Verifier decision.
- Trace summary.

### 6. Show AMD/Qwen Proof

Briefly show:

- `/health` response.
- vLLM model name.
- GPU/ROCm readiness output.
- Eval output.

## Expected Claims

Use these exact claims in the video:

- "This is an agentic audit workflow, not a chat wrapper."
- "Each stage has its own context, artifact, and tool boundary."
- "The verifier can force a degraded decision when evidence is missing."
- "The public UI makes agent work visible to judges."
- "The target runtime is Hugging Face Space frontend plus AMD-hosted Qwen through vLLM."

## Do Not Claim

- Do not claim the system fully reproduces experiments automatically.
- Do not claim all papers can be verified with perfect evidence.
- Do not claim the mock runtime is the final AMD model run.
- Do not hide failed resolvers; they are part of the product value.
