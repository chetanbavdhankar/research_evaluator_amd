# Technology Stack

## Purpose

This document fixes the technology choices for the system. Every implementation decision that touches a library, framework, or external service is locked here. When a coding agent is unsure which library to use for a task, it consults this document before deciding. New tools are added only by updating this document.

---

## Core Reasoning

### Language Model Inference

**vLLM serving open-weight models on AMD ROCm.**

- Inference server: vLLM with ROCm backend
- Endpoint: OpenAI-compatible HTTP API at `http://localhost:8000/v1`
- Primary model: Qwen3.6 (32B or 14B depending on VM GPU memory)
- Fallback model: Gemma 4 (for comparison or if Qwen is unavailable)
- Client library: `openai` Python SDK pointed at the vLLM endpoint, since vLLM speaks the OpenAI-compatible API

All LLM calls go through a single thin wrapper in `src/tools/vllm_client.py` that handles retries, timeouts, and structured-output extraction. No agent calls vLLM directly.

### Why open-weight on AMD
- The hackathon runs on AMD infrastructure with $100 of credits — using the local vLLM server avoids spending credits on external API calls
- All reasoning is auditable and fully under our control
- No data leaves the VM, which simplifies handling of paper PDFs and downloaded datasets

---

## Agent Orchestration

### Agent Framework

**LangGraph.**

- Provides explicit `StateGraph` abstraction matching our phase-based pipeline
- Native checkpointing for resumability
- Conditional edges support our success / partial / blocked routing
- Mature ecosystem and active development
- Python-native, no separate runtime

Within LangGraph, individual agents are simple Python functions, not LangChain `Runnable` chains. We use LangGraph for orchestration, not LangChain for prompting. This keeps the codebase lean and avoids LangChain's frequent breaking changes.

### Why not CrewAI / AutoGen
- CrewAI's strength is conversational multi-agent collaboration; our system is sequential and structured
- AutoGen is heavier and more general; we need a focused state-graph executor

---

## Data and Schemas

### Schema Definition

**Pydantic v2.**

- All inter-phase artifacts are Pydantic models
- Strict mode enabled — unknown fields are rejected
- Models are defined once in `src/schemas/` and imported by all consumers
- Validation happens automatically on instantiation and on JSON load
- Models export to JSON Schema for documentation and external validation

### Serialization

**JSON for all artifacts.**

- Every phase output is a JSON file
- Pydantic's `model_dump_json()` for writing, `model_validate_json()` for reading
- Pretty-printed with 2-space indent for human readability
- Datetime fields use ISO 8601 strings

### State Store

**Filesystem-based, JSON files.**

- One run directory per pipeline execution
- Each phase output is a single JSON file
- A `pipeline_state.json` tracks global state
- No database, no external state service
- Inspection is trivial (any text editor)

---

## Paper Ingestion

### PDF Parsing

**PyMuPDF (`pymupdf` package).**

- Fast, well-maintained, handles complex academic layouts well
- Extracts text with layout information (useful for distinguishing tables, figures, captions)
- Extracts embedded images
- Handles encrypted PDFs gracefully

Fallback: `pdfplumber` for tables when PyMuPDF's text extraction misses tabular structure.

### HTML Parsing

**`beautifulsoup4` with `lxml` parser.**

- Standard, robust, handles arXiv abstract pages and journal HTML well
- For arXiv, prefer the abstract page HTML over the PDF when both are available, as it is cleaner and machine-friendly

### arXiv Integration

**`arxiv` Python package.**

- Resolves arXiv IDs to metadata (title, authors, abstract, PDF URL)
- Downloads PDFs to local disk
- Used as the entry point when input is an arXiv URL

---

## Web Search and HTTP

### Web Search

**Tavily API for general search; direct API integrations for specialized repositories.**

- Tavily is purpose-built for LLM-driven search, returns clean structured results
- Free tier is sufficient for hackathon scope
- Specialized repositories use direct integrations:
  - Hugging Face Datasets: `datasets` library
  - Kaggle: `kaggle` CLI/API
  - UCI ML Repository: HTTP scraping with `requests`
  - Zenodo: Zenodo REST API
  - GitHub: `PyGithub`

### HTTP Fetching

**`httpx`.**

- Modern, async-capable, supports both sync and async patterns
- Used for all dataset downloads
- Configured with reasonable timeouts (30s connect, 600s total) and retries

---

## Data Handling

### Tabular Data

**`pandas` for analysis, `polars` for large-scale operations.**

- pandas is the lingua franca and what most papers use, so reproducibility benefits from sticking with it
- polars is used only when datasets exceed memory or pandas becomes the bottleneck

### Numerical Computation

**`numpy`, `scipy`.**

Standard. Pinned to versions compatible with the deep learning frameworks installed in the reconstructed environment for the paper being replicated.

### Machine Learning

**Whatever the paper uses.**

The deep learning framework (PyTorch / TensorFlow / JAX), classical ML library (scikit-learn / XGBoost / LightGBM), and any specialized libraries are determined per-paper by Phase 3 (Environment Reconstruction). The pipeline itself does not commit to a specific ML library.

The orchestrator's own Python environment includes:
- PyTorch (for any agent that needs it directly, rare)
- scikit-learn (for validation utilities)
- transformers and datasets (for Hugging Face dataset access)

---

## Code Execution

### Execution Mechanism

**Direct subprocess execution on the VM.**

- Generated code is written to `artifacts/code/phase{N}/script.py`
- Executed via `subprocess.run([python_executable, script.py], ...)`
- Python executable is the one provisioned by Phase 3 in a conda environment
- stdout, stderr, exit code, and runtime captured into `ExecutionResult` records

### Environment Provisioning

**Conda (Miniconda) for environment management.**

- Phase 3 produces an `environment.yml` and creates a named conda environment
- Subsequent code execution uses that environment's Python interpreter
- Environments are named `repro_run_{timestamp}` and cleaned up at the end of the run

### Why not Docker
- Hackathon time pressure favors direct execution
- The VM is single-tenant for the hackathon, so isolation across runs is less critical
- Adds setup complexity without proportional benefit at this scale

If hardening is needed later, swapping subprocess execution for containerized execution touches only `src/tools/code_execution.py`.

---

## Visualization

### Figures Reproduced from Papers

**`matplotlib` and `seaborn`.**

- The default for scientific Python papers, so reproductions naturally use these
- Generated code in Phase 5 uses whatever the paper used; if the paper used Plotly or ggplot, the generated code uses that

### Final Report Visualizations

**`matplotlib` for static plots, `plotly` for any interactive elements in HTML report.**

The final report PDF uses static matplotlib only.

---

## Report Generation

### PDF Generation

**`reportlab`.**

- Programmatic, no LaTeX dependency, runs anywhere
- Used to render the final reproducibility report

### Markdown Rendering (for intermediate outputs)

**`mistune` for parsing, custom renderer for HTML output.**

Used when generating HTML versions of phase summaries during development.

---

## Logging and Observability

### Logging

**Python standard `logging` module with structured format.**

- One logger per module
- Default level INFO; DEBUG enables full LLM prompt/response logging
- Logs written to `artifacts/logs/phase{N}.log` per phase, plus aggregated `pipeline.log`
- Format: `{timestamp} {level} {phase} {agent} {message}`

No external logging service. No structured event store.

---

## Testing

### Unit Tests

**`pytest`.**

- Tests live in `tests/`
- Each phase has a corresponding test module
- Sample papers in `tests/fixtures/` cover at least one ML paper, one statistical paper, one mixed paper

### Integration Tests

**End-to-end tests on a small set of curated papers.**

- Runs full pipeline against a fixture paper
- Asserts on phase output schemas (must validate) and key extracted fields (must match expected)
- Slow; not run on every commit; run before demo

---

## Configuration and CLI

### CLI Framework

**`typer`.**

- Type-hinted, derives CLI from function signatures
- Lightweight, no boilerplate
- Entry point: `python -m research_repro <paper_url>` or installed as `repro <paper_url>`

### Configuration

**Pydantic Settings (`pydantic-settings`).**

- Loads config from `config.json`, environment variables, or CLI flags
- Validated on load
- Single source of truth for all run parameters

---

## Dependencies Summary

The orchestrator's own `pyproject.toml` declares (approximate, exact versions pinned at implementation time):

```
# Core
langgraph
pydantic >= 2.0
pydantic-settings
typer
httpx

# LLM client
openai

# Paper parsing
pymupdf
pdfplumber
beautifulsoup4
lxml
arxiv

# Search and data sources
tavily-python
datasets
kaggle
PyGithub

# Data and ML
pandas
numpy
scipy
scikit-learn
matplotlib
seaborn

# Reporting
reportlab
mistune

# Testing
pytest
pytest-asyncio
```

The replication environments (per paper, provisioned by Phase 3) have their own dependencies separate from this list.

---

## Version Pinning Policy

For the orchestrator's own dependencies:
- All dependencies pinned to a specific minor version in `pyproject.toml`
- A `uv.lock` or equivalent lockfile committed to the repository
- Updates are deliberate, not automatic

For the replication environments:
- Versions are determined by Phase 3 from the paper's specifications
- Conservative resolution is preferred (oldest compatible version)
- Pinned in the `environment.yml` produced by Phase 3

---

## What This Document Does Not Cover

- Specific prompt templates (those live in each `phases/phase{N}_*/prompts.py`)
- Specific schema field definitions (those live in `SCHEMAS.md` and `src/schemas/`)
- Deployment infrastructure (single VM for hackathon; if expanded, a separate `DEPLOYMENT.md` will be added)

---

## Decision Log

When a stack choice is contested or revisited, log the decision here:

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-07 | vLLM on AMD ROCm for inference | User direction; aligns with hackathon hardware |
| 2026-05-07 | LangGraph for orchestration | State graph fits sequential phase model; native checkpointing |
| 2026-05-07 | Pydantic v2, strict mode, JSON serialization | Single source of truth for inter-phase contracts |
| 2026-05-07 | Direct subprocess execution, no Docker | User preference; hackathon simplicity |
| 2026-05-07 | Conda for replication environments | Standard in scientific Python; handles non-Python deps |
