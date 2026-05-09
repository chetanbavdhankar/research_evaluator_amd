# REPLICABILITY-AUDIT

A production-grade CLI tool to autonomously audit scientific research papers (specifically astronomy) for data and methodological replicability.

## Start Here: Agentic Reproducibility Engine

[`agentic-reproducibility-engine/`](agentic-reproducibility-engine/) is the separate AMD/Qwen multi-agent reproducibility evaluator.

Use that folder when you want the full agentic product: static HTML frontend, FastAPI backend, multi-agent audit graph, live arXiv/DOI/GitHub/dataset resolvers, verifier objections, report provenance, and an eval harness for agent behavior.

It is intentionally separate from the existing CLI/wiki implementations so users can tell immediately which path is the interactive agentic system.

## Repository Map

| Path | Purpose |
| --- | --- |
| `agentic-reproducibility-engine/` | New standalone agentic system for AMD/Qwen paper reproducibility audits. |
| `cb/`, `cb1/`, `src/replicability_audit/` | Existing CLI and staged evaluator implementations. |
| `llm-wiki/` | Knowledge base, architecture notes, and supporting context. |

## Overview
This tool ingests a research paper (PDF or arXiv URL), extracts data assets, method pipelines, and software inventory using an LLM (Gemini or local Ollama), mathematically scores the methodology, and produces a structured JSON audit alongside an executable replication scaffold.

## Architecture
The system enforces strict determinism, heavily limiting LLM hallucinations by isolating them exclusively to text-to-JSON parsing stages.
- **Stage 0 (Ingest)**: Downloads and parses PDF layout to text.
- **Stage 1 (Extraction)**: Uses LLMs (Ollama/Gemini) forced into strict JSON mode to parse data assets, methodology, software, and compute footprint.
- **Stage 2 (Resolution)**: Pure Python adapters resolve extracted data items against known APIs (e.g., AstroQuery, Zenodo, GitHub) and generate executable `FetchScripts`.
- **Stage 3 (Scoring)**: Evaluates the pipeline across an 8-axis scorecard and assigns a Tier (1-3).
- **Stage 4 (Plan)**: Uses Jinja2 templates and LLM prose synthesis to assemble a markdown replication report.
- **Stage 5 (Scaffold)**: Deterministic codegen creating a `paper_audits/<id>/05_scaffold` directory with runnable Python data fetching scripts and analysis skeletons.

## Setup Instructions
1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Add your API key to the `.env` file if you plan to use Google Gemini instead of Ollama:
```
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

## Usage Examples
```bash
# Ingest, extract, resolve, and score only (Stages 0-3)
python main.py ingest 2605.05650

# Run full pipeline and generate executable Python scaffold (Stages 0-5)
python main.py plan https://arxiv.org/abs/2605.05650 --exec
```

## Recent Changes
- **v0.1 Completed**: Successfully implemented Stages 0 through 5 including extraction, resolution adapters, mathematical scoring, and scaffold code generation.
- Re-architected output to a unified directory structure (`paper_audits/<paper_id>/`).
- Fixed Ollama `qwen` integration by extending `num_ctx` context window to 16,384 tokens to support full paper processing without `EOF` crashes.
- Implemented `benchmark/` test suite ensuring extraction accuracy against hand-curated ground truths.

## Technical Debt Log
- **M7 Benchmark Expansion**: The validation harness is active but the ground truth dataset currently only contains 1 paper. Needs expansion to 25 papers.
- **Table Extraction**: `pdfplumber` integration is currently deferred in favor of raw text chunking; this limits Stage 0's ability to cleanly detect tabulated data.
- **Code validation execution**: The `04_validate.py` script is generated as a skeleton. Future iterations will require it to programmatically execute and compare results against extracted tables.
