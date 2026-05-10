# Submission Form Copy

Use this as the paste-ready source for the lablab.ai submission fields.

## Project Title

Agentic Reproducibility Engine

## Short Description

AMD-hosted multi-agent research reproducibility evaluator that reads papers, resolves arXiv/DOI/GitHub/dataset evidence, critiques gaps, and streams audit-ready reports.

## Long Description

Research papers often claim reproducibility while leaving critical evidence scattered across PDFs, arXiv records, DOI metadata, GitHub repositories, datasets, and informal implementation notes. The Agentic Reproducibility Engine turns that messy audit process into a visible multi-agent workflow.

Users submit a paper or paper reference through a static web interface. The backend runs a sequence of specialized agents that plan the audit, extract claims and artifacts, retrieve external evidence, score reproducibility risk, design a replication plan, generate code/data follow-up commands, and critique unsupported assumptions before writing the final report. The UI streams the work live so judges can inspect agent artifacts, tool calls, resolver outcomes, verifier objections, and final provenance.

The target deployment uses a Hugging Face Static Space as the public frontend and an AMD Developer Cloud instance as the backend. The AMD host serves `Qwen/Qwen3.5-27B` through vLLM on ROCm and runs the FastAPI agent API. The system is designed to fail closed: if arXiv, DOI, GitHub, or dataset evidence cannot be verified, the report records that gap and degrades the decision rather than inventing placeholder evidence.

The project includes a public GitHub repo, self-serve AMD/Hugging Face deployment kit, deterministic eval harness, static frontend, API backend, live evidence resolver tools, and an audit trace format for reproducibility evidence.

## Technology & Category Tags

- AI Agents & Agentic Workflows
- AMD Developer Cloud
- ROCm
- AMD Instinct MI300X
- Hugging Face
- Hugging Face Spaces
- Qwen
- vLLM
- FastAPI
- Multi-agent systems
- Research reproducibility
- Tool calling
- Evidence retrieval
- Eval harness

## Public GitHub Repository

https://github.com/chetanbavdhankar/research_evaluator_amd

## Main Code Path

https://github.com/chetanbavdhankar/research_evaluator_amd/tree/main/agentic-reproducibility-engine

## Demo Application Platform

Hugging Face Static Space frontend connected to an AMD Developer Cloud FastAPI backend.

## Application URL

TODO: add Hugging Face Space URL after deployment.

Recommended format:

```text
https://<space-name>.hf.space/?api=https://<amd-backend-host>
```

## Video Presentation URL

TODO: add final MP4/video URL after recording.

## Slide Presentation

Use `presentation/slides.html` and export it to PDF before upload.

## Cover Image

Use `assets/cover-image.png`.

## One-Line Judge Summary

An AMD/Qwen-powered multi-agent system that makes research reproducibility audits inspectable: every plan, tool call, evidence gap, verifier objection, and final decision is streamed and preserved.

## Track Fit

Track 1: AI Agents & Agentic Workflows.

This is not a single prompt or RAG wrapper. It coordinates specialized agents, validates tool requests, calls live evidence resolvers, allows verifier repair at higher autonomy levels, and exposes the full trace to users.
