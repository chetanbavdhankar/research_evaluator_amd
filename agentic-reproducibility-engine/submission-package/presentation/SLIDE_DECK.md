# Slide Deck Source

Export `slides.html` to PDF for the lablab submission.

## Slide 1 — Agentic Reproducibility Engine

AMD-hosted multi-agent research reproducibility evaluator powered by Qwen, vLLM, ROCm, and Hugging Face Spaces.

## Slide 2 — Problem

Research teams need to know whether a paper can be reproduced, but evidence is scattered across PDFs, arXiv, DOI metadata, GitHub repositories, datasets, and informal notes.

Manual audits are slow, inconsistent, and often hide uncertainty.

## Slide 3 — Solution

The product turns reproducibility review into a visible multi-agent workflow.

Users submit a paper, choose autonomy, watch the trace, inspect evidence, and receive an audit-ready report.

## Slide 4 — Agentic Workflow

The system plans, reads, retrieves, scores, plans experiments, generates code/data follow-up, verifies assumptions, and writes the report.

Each stage has its own context, model artifact, tool access boundary, and trace output.

## Slide 5 — AMD Architecture

Static Hugging Face Space frontend connects to a FastAPI backend on AMD Developer Cloud.

The backend calls Qwen/Qwen3.5-27B through vLLM on ROCm.

## Slide 6 — Evidence Tools

Live tools resolve arXiv, DOI, GitHub, and dataset evidence.

Missing evidence becomes an explicit gap. The verifier can degrade the decision.

## Slide 7 — Demo Flow

Submit paper -> autonomy slider -> live trace -> evidence panel -> verifier objections -> final report.

The judge can inspect the work, not just the answer.

## Slide 8 — Evaluation

The eval harness checks agent contracts and overall audit success.

It grades prompts, contexts, model artifacts, tool calls, resolver coverage, verifier behavior, report provenance, and placeholder-evidence bans.

## Slide 9 — Business Value

Target users: research labs, ML teams, funders, reviewers, benchmark maintainers, and enterprise AI teams.

Value: faster first-pass audits with transparent provenance and concrete replication next steps.

## Slide 10 — Roadmap

Deploy AMD/Qwen backend, publish HF Space, add more resolver sources, expand eval cases, support paper PDFs, and collect user feedback from research teams.
