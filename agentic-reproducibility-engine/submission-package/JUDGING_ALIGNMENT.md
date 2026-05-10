# Judging Alignment

## Application Of Technology

The project demonstrates AMD compute through an end-to-end agentic workflow:

- Hugging Face model: `Qwen/Qwen3.5-27B`.
- Serving layer: vLLM OpenAI-compatible endpoint.
- Compute target: AMD Developer Cloud with ROCm and MI300X-class GPUs.
- App layer: FastAPI agent backend plus static Hugging Face Space frontend.
- Tool layer: arXiv, DOI, GitHub, dataset, scoring, code/data planning, verifier, and report writer tools.
- Eval layer: deterministic agent and whole-audit checks.

The model is not used as a generic chatbot. It powers separate audit agents with scoped contexts, tool access boundaries, and visible outputs.

## Presentation

The product has a clear demo path:

1. Submit a paper.
2. Choose autonomy level.
3. Watch the live audit trace.
4. Inspect evidence resolver outcomes.
5. Review verifier objections.
6. Read the final audit-ready report.

The slide deck and video should focus on that path instead of showing setup commands.

## Business Value

The target users are:

- Research teams checking reproducibility before publication.
- Labs and funders reviewing claims before investing in replication.
- ML engineers evaluating papers before adopting methods.
- Conference reviewers and benchmark maintainers.
- Enterprise AI teams auditing research-derived systems.

The value is faster triage with explicit provenance. It does not claim to prove full reproducibility automatically; it reduces time-to-first-audit and makes gaps visible.

## Originality

The distinctive product idea is verifier-driven reproducibility auditing:

- The system streams intermediate agent artifacts instead of hiding work in a final answer.
- Evidence resolvers are live tools, not placeholder links.
- The verifier can degrade the final decision when provenance is missing.
- The autonomy slider gives users control over how much the system can do.
- The eval harness grades agent contracts, not just final prose.

## Track 1 Fit

Track 1 asks for AI agents and agentic workflows. This project fits because it coordinates a multi-agent research audit workflow with visible planning, tool calls, verification, and reporting.

## Honest Limits To State

- A reproducibility audit is a decision-support workflow, not a guarantee that results can be reproduced.
- Live resolver quality depends on external metadata availability.
- Full AMD/Qwen proof requires running the package on an AMD GPU host.
- The static frontend can run anywhere, but the target submission should point to an AMD-hosted backend.
