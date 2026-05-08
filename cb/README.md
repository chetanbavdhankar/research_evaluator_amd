# Autonomous Research Reproducibility Engine

The Autonomous Research Reproducibility Engine is an agentic framework designed to ingest research papers (via arXiv HTML/PDF) and systematically replicate their methodology, data preprocessing, and analysis execution.

It operates in a strict, multi-phase pipeline driven by LangGraph and Pydantic schemas to ensure high-fidelity, grounded extraction.

## Architecture

The engine runs as a LangGraph state machine with the following phases:

1. **Phase 1: Paper Comprehension**
   - Parses arXiv HTML/PDF.
   - Extracts a strict `PaperKnowledgeArtifact` (Metadata, Summary, Datasets, Preprocessing, Methodology, Results, Conclusions).
   - Features a dual-layer verification loop (Deterministic exact-quote matching + LLM Coherence fallback).
2. **Phase 2: Data Sourcing**
   - Classifies datasets (Public, Proprietary, etc.).
   - Autonomously generates download scripts and retrieves public datasets into a local `runs/<run_id>/data/` sandbox.
3. **Phase 3: Environment Reconstruction**
   - Infers required libraries and dependencies (e.g., PyTorch version based on year).
   - Provisions a strict Conda environment specifically for the paper.
4. **Phase 4: Data Processing Replication**
   - Generates and executes preprocessing scripts mirroring the paper's methodology inside the Conda sandbox.
5. **Phase 5: Analysis & Method Execution**
   - Implements the model architecture, training, and evaluation scripts.
   - Executes multi-seed runs for unseeded methodologies.
6. **Phase 6: Results Validation** (Pending)
   - Compares locally executed results with the paper's reported numbers.

## Setup

1. **Prerequisites**
   - Python 3.12+
   - `uv` package manager
   - Conda (optional but recommended for Phase 3-5 execution)

2. **Environment**
   Copy `.env.example` to `.env` and fill in your LLM API keys:
   ```bash
   LLM_API_KEY=your_key
   LLM_ENDPOINT=https://api.openai.com/v1
   LLM_MODEL=gpt-4o
   ```

## Usage

Use the provided Typer CLI to run the pipeline. You can provide an arXiv URL or a local path to a PDF file:

### Using an arXiv URL:
```bash
uv run python -m research_repro.cli run https://arxiv.org/html/2605.04781v1
```

### Using a Local PDF:
```bash
uv run python -m research_repro.cli run "C:/path/to/your/paper.pdf"
```

A new directory will be created in `runs/run_<timestamp>_<slug>/` containing all generated artifacts, logs, data, and scripts.

## Milestones Implemented
- **M1:** Scaffolding & Base Tooling
- **M2:** Phase 1 (Paper Comprehension) & Orchestrator Skeleton
- **M3:** Phase 2 (Data Sourcing) & Phase 3 (Environment Reconstruction)
- **M4:** Phase 4 (Data Processing) & Phase 5 (Analysis Execution)
- **M5:** Phase 6 (Results Validation)
