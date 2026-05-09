# Differentiation

The Agentic Reproducibility Engine is not a chat wrapper and not another static wiki page. It is a runnable agentic audit system designed to show autonomous research-evaluation work as it happens.

## What Makes It Different

| Capability | Agentic Reproducibility Engine | Typical static evaluator |
| --- | --- | --- |
| User experience | Static HTML app with live trace, controls, and report panels | Static page, notebook, or single chat box |
| Runtime | FastAPI backend with a multi-agent state graph | One prompt or deterministic script |
| Agent behavior | Separate context, model call, tool access, and artifact per audit stage | Blended reasoning with unclear ownership |
| Evidence | Live arXiv, DOI, GitHub, and dataset resolvers | Prepared links or placeholder evidence |
| Verification | Critic/verifier can object and force decision degradation | Final answer usually accepted as-is |
| Autonomy | End-user slider controls how much the system can do | Fixed behavior |
| Evaluation | Agent-level and overall audit eval harness | Manual inspection only |

## Product Contract

The system should make five things visible in every meaningful run:

1. What the system plans to evaluate.
2. What evidence it retrieved or failed to retrieve.
3. Which tool calls were requested and allowed.
4. Where the verifier challenged weak assumptions.
5. Why the final reproducibility decision was reached.

## Submission Positioning

Frame this folder as:

> An AMD-hosted multi-agent research reproducibility evaluator powered by Qwen3.5-27B on ROCm/vLLM. The system reads a paper, retrieves external evidence, calls deterministic audit tools, critiques its own assumptions, and produces an audit-ready reproducibility report with provenance.

The existing `llm-wiki/` content remains useful background material. This folder is the product implementation.
