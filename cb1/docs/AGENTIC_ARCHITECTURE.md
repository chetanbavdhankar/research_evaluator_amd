# SpecCurve Agentic Architecture

## Mission

SpecCurve should not be a fixed LaLonde demo. For an AI agents hackathon, the product
needs to show an LLM agent constructing a reproduction workflow for an unfamiliar empirical
paper, then handing that plan to verifiers and execution tools.

The working principle is:

```text
LLM proposes. Deterministic systems verify. AMD MI300X accelerates the heavy evidence loop.
```

## Karpathy-Inspired Design Rules

- Software 3.0 layer: use natural language and paper text as the programming interface.
- Verifiability layer: every agent output must be resettable, efficient to retry, and
  rewardable by automated checks.
- Partial autonomy: agents may plan and generate artifacts, but executable steps run in a
  sandbox and are blocked by verifier failures.
- Evidence over prose: a report can summarize, but it cannot be the evidence.

## Runtime Flow

```text
paper text or URL
-> Paper/workflow planning prompt
-> OpenAI-compatible LLM endpoint
-> workflow-plan.json
-> deterministic verification-report.json
-> sandbox execution layer
-> dynamic robustness/specification grid
-> AMD MI300X benchmark and robustness artifacts
-> final evidence report
```

## New L0 Agentic Files

- `speccurve_l0/llm_client.py` - small OpenAI-compatible client for Ollama, vLLM, or hosted APIs.
- `speccurve_l0/agentic_schema.py` - strict workflow-plan schema and parser.
- `speccurve_l0/agentic_planner.py` - Software 3.0 planning prompt.
- `speccurve_l0/agentic_verifier.py` - deterministic checks and score.
- `scripts/plan_reproduction.py` - CLI for producing `workflow-plan.json` and
  `verification-report.json`.

## Environment

```bash
SPECCURVE_LLM_ENDPOINT=http://localhost:11434/v1
SPECCURVE_LLM_MODEL=qwen3.5:4b
SPECCURVE_LLM_API_KEY=none
```

For the AMD path, set `SPECCURVE_LLM_ENDPOINT` to a vLLM OpenAI-compatible endpoint on
the MI300X host.

## What Remains Deterministic

The existing SpecCurve L0 pipeline remains useful, but it moves down the stack:

- dataset card and hashes
- predeclared or verifier-approved spec grid
- invalid-spec rejection
- robustness surface generation
- benchmark contract
- public-copy lint

The demo should lead with the agent planner, then show how the deterministic core prevents
the LLM from inventing unsupported evidence.
