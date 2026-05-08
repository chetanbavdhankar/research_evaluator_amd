# Implementation Plan — Autonomous Research Reproducibility Engine

> **Audience:** a coding agent (or human engineer) building this project from scratch.
> **Spec source:** `llm-wiki/` (12 markdown files at the top level). Treat this as canonical; ignore `llm-wiki/archive/`, `llm-wiki/Knowledge_base/`, and `llm-wiki/kiran/`.
> **Repo:** existing repo at `research_evaluator_amd/`. Code is added alongside `llm-wiki/`.
> **Target paper for first end-to-end run:** [arXiv 2605.04781](https://arxiv.org/abs/2605.04781).

---

## 0. Mission

Build an end-to-end multi-agent system that takes a research paper (PDF / HTML / arXiv link) and produces a structured reproducibility report. The system runs as a six-phase sequential pipeline orchestrated by LangGraph. Each phase produces a Pydantic-validated JSON artifact consumed by the next phase. The final deliverable is a PDF + JSON reproducibility report.

**Single model architecture.** One LLM handles all reasoning (analysis, code generation, evaluation). Phase 6 comparisons are primarily deterministic (threshold-based classification), with the LLM used only for narrative synthesis and discrepancy attribution.

**Two deployment modes**, switched by config only:

| Mode | LLM | Endpoint |
|------|-----|----------|
| **Local dev** | Ollama `qwen3.5:4b` | `http://localhost:11434/v1` |
| **Production (AMD VM + HF Spaces)** | `Qwen3.6-27B` on vLLM | `http://<amd-vm-ip>:8000/v1` |

**Deployment architecture:**
- **Hugging Face Space** runs the full orchestrator, Gradio UI, and CPU-bound replication code (pandas/scipy for ~10⁵ rows)
- **AMD VM** provides two services: (1) vLLM on port 8000 for LLM inference, (2) GPU compute API on port 8001 for bootstrap CIs, permutation tests, and specification robustness analysis on MI300X
- The AMD VM is accessed solely via its public IP address — no API key, no SSH

The agent **must not** code against any model-specific quirk. All inference is OpenAI-compatible JSON mode, schema-validated, retried on parse failure.

---

## 1. Required Reading (Do First, In Order)

The agent must read these files **before writing any code**. Do not skip.

1. `llm-wiki/README.md` — index and reading order
2. `llm-wiki/phase0_project_overview.md` — *why*: design principles, scope boundaries
3. `llm-wiki/ARCHITECTURE.md` — runtime architecture, orchestrator, state store, recovery
4. `llm-wiki/STACK.md` — locked technology choices (do not substitute)
5. `llm-wiki/SCHEMAS.md` — Pydantic schemas; **the canonical contract**
6. `llm-wiki/GLOSSARY.md` — terminology, naming conventions
7. `llm-wiki/phase1_paper_comprehension.md` through `llm-wiki/phase6_results_validation.md` — methodology per phase

When implementing a specific phase, the agent loads that phase's methodology doc + `SCHEMAS.md` + `ARCHITECTURE.md` into active context.

---

## 2. Standing Rules (Apply Throughout)

These rules are non-negotiable. Violating any one of them creates rework.

1. **Schema is the contract.** If a phase doc and `SCHEMAS.md` disagree, follow the schema and flag the inconsistency in a comment. Pydantic models in `src/research_repro/schemas/` are the canonical implementation.
2. **No model-specific prompt tricks.** Treat the LLM as "any OpenAI-compatible chat model that returns JSON." If a prompt only works with one model, it's wrong.
3. **Strict Pydantic v2.** `model_config = ConfigDict(extra="forbid", strict=True)` on every model. Validation failures are bugs.
4. **JSON for all artifacts.** Every phase output is a single JSON file written via `model_dump_json(indent=2)`.
5. **Stateless tools, structured failures.** Tools never hold state. Failures return `ExecutionFailure`/`HumanInterventionFlag` records, never raise unhandled exceptions out of agents.
6. **Retry-on-parse-failure for all LLM calls.** Up to 3 attempts. After 3, surface the raw response and a `ValidationError` to the caller.
7. **Naming conventions** (from `GLOSSARY.md`):
   - Classes: `PascalCase`
   - Variables, functions, JSON fields: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Phase doc files: `lower_case.md`; top-level docs: `UPPER_CASE.md`
8. **Conservative defaults when forced to assume.** Library defaults > paper-likely values. Document every assumption as an `AmbiguityFlag`.
9. **Fail loudly.** Never silently skip a step. Every gap is a flag.
10. **Trace everything.** Every artifact field that came from the paper has a `paper_quote` and `location_in_paper`.
11. **No `.env` secrets in git.** `.env` is gitignored. Use `pydantic-settings` to load.
12. **Conda env name convention.** `repro_run_{timestamp}` per-paper environment, separate from the orchestrator's own env.
13. **Per-phase logs** under `runs/<run_id>/artifacts/logs/phase{N}.log`. Format: `{ts} {level} {phase} {agent} {message}`.
14. **Verify every agent output.** Every `BaseAgent.run_structured()` call passes through a two-layer verification gate before returning:
    - **Layer 1 (deterministic, zero cost):** quote grounding (fuzzy-match `paper_quote` fields against source text), value-range checks, completeness checks, cross-field consistency.
    - **Layer 2 (LLM coherence, one cheap call):** a focused verification prompt asking whether the output is grounded, relevant, and internally coherent. Receives only the output + a short source excerpt, not the full paper.
    - Failures inject the reason into a retry prompt. After 3 total attempts (extraction + verification retries combined), surface the best partial result with a `VerificationFailure` flag.
    - Every successful return includes a `VerificationRecord` (checks run, pass/fail, attempt count) persisted alongside the phase output.

---

## 3. Environment & Prerequisites

### 3.1 Local development machine (Windows)

Install once:

| Tool | Why | How |
|------|-----|-----|
| Python 3.11 | Orchestrator runtime | `winget install Python.Python.3.11` or python.org installer |
| `uv` | Fast Python package manager | `pip install uv` or `winget install astral-sh.uv` |
| Miniconda | Per-paper replication environments (Phase 3) | https://docs.conda.io/en/latest/miniconda.html |
| Ollama | Local LLM serving (OpenAI-compatible) | https://ollama.com/download |
| Git | Version control | (already installed) |

After installing Ollama, pull the model:

```powershell
ollama pull qwen3.5:4b
```

> If `qwen3.5:4b` is not available on Ollama, fall back to `qwen2.5:7b` and update `.env` accordingly. Surface this to the user before proceeding.

### 3.2 API keys / secrets (used in Phase 2)

Create a `.env` file at repo root (gitignored):

```
TAVILY_API_KEY=...
KAGGLE_USERNAME=...
KAGGLE_KEY=...
GITHUB_TOKEN=...
HF_TOKEN=...                # optional, for HF Datasets gated content

LLM_ENDPOINT=http://localhost:11434/v1
LLM_MODEL=qwen3.5:4b
LLM_API_KEY=none             # Ollama ignores this; set to "none" for keyless vLLM

AMD_COMPUTE_ENDPOINT=       # empty for local dev; http://<amd-vm-ip>:8001 in production
```

For production on HF Spaces, set as Space secrets: `LLM_ENDPOINT=http://<amd-vm-ip>:8000/v1`, `LLM_MODEL=Qwen3.6-27B`, `AMD_COMPUTE_ENDPOINT=http://<amd-vm-ip>:8001`. No API key needed — the AMD VM uses a public IP with open ports for the hackathon. The user must request any keys they don't have; the agent should never invent keys.

### 3.3 Repo bootstrap

The agent's first action after reading the spec is to initialize the Python project:

```powershell
uv init --package research-repro --no-readme
# Edit pyproject.toml per §4.2
uv sync
```

---

## 4. Repository Layout (Target End State)

```
research_evaluator_amd/                    # repo root
├── llm-wiki/                              # spec (existing — DO NOT MODIFY without §5 approval)
├── IMPLEMENTATION_PLAN.md                 # this file
├── README.md                              # short user-facing readme (write last)
├── pyproject.toml
├── uv.lock
├── .env.example                           # template, no real values
├── .env                                   # gitignored, real values
├── .gitignore                             # add: .env, runs/, .venv/, __pycache__/, *.egg-info/
│
├── src/research_repro/
│   ├── __init__.py
│   ├── cli.py                             # typer entry point
│   ├── config.py                          # pydantic-settings; loads .env + config.json
│   ├── orchestrator.py                    # LangGraph StateGraph
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py                      # CitationDependency, AmbiguityFlag, ExecutionFailure, HumanInterventionFlag, ProvenanceRecord, VerificationRecord
│   │   ├── paper_knowledge.py             # PaperKnowledgeArtifact + sub-models
│   │   ├── data_manifest.py
│   │   ├── environment_spec.py
│   │   ├── processed_dataset.py
│   │   ├── analysis_results.py
│   │   ├── reproducibility_report.py
│   │   └── pipeline_state.py              # PipelineState, PhaseStatus
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                        # BaseAgent: run_structured() with two-layer verification gate
│   │   ├── verification.py                # deterministic checks (quote grounding, range, completeness) + LLM coherence check
│   │   ├── reader.py
│   │   ├── searcher.py
│   │   ├── coder.py
│   │   ├── executor.py                    # runs subprocess, returns ExecutionResult
│   │   ├── validator.py
│   │   └── reporter.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── llm_client.py                  # single-endpoint LLM client
│   │   ├── pdf_parser.py                  # PyMuPDF wrapper
│   │   ├── html_parser.py                 # BeautifulSoup wrapper
│   │   ├── arxiv_fetcher.py               # arxiv package wrapper
│   │   ├── web_search.py                  # tavily wrapper
│   │   ├── http_fetch.py                  # httpx wrapper with retries
│   │   ├── code_execution.py              # subprocess.run with timeout/memory cap
│   │   ├── conda_env.py                   # create / activate / verify conda env
│   │   ├── gpu_compute.py                 # client for AMD VM GPU compute API (bootstrap, permutation, robustness)
│   │   ├── deterministic_comparison.py    # threshold-based result classification (no LLM needed)
│   │   ├── data_repos/
│   │   │   ├── huggingface.py
│   │   │   ├── kaggle.py
│   │   │   ├── zenodo.py
│   │   │   ├── github.py
│   │   │   └── sdss.py                    # SDSS DR16 data access (target paper)
│   │   └── report_pdf.py                  # reportlab PDF generation
│   │
│   ├── phases/
│   │   ├── __init__.py
│   │   ├── phase1_paper_comprehension/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py
│   │   │   └── prompts.py
│   │   ├── phase2_data_sourcing/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py
│   │   │   └── prompts.py
│   │   ├── phase3_environment_reconstruction/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py
│   │   │   └── prompts.py
│   │   ├── phase4_data_processing/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py
│   │   │   └── prompts.py
│   │   ├── phase5_analysis_execution/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py
│   │   │   └── prompts.py
│   │   └── phase6_results_validation/
│   │       ├── __init__.py
│   │       ├── executor.py
│   │       ├── prompts.py
│   │       └── report_generator.py
│   │
│   └── logging_setup.py
│
├── runs/                                  # gitignored; generated per execution
│   └── run_<timestamp>_<paper-slug>/
│       ├── config.json
│       ├── pipeline_state.json
│       ├── phase1_output.json ...
│       ├── final_report.pdf
│       ├── final_report.json
│       └── artifacts/
│           ├── data/
│           ├── code/
│           ├── figures/
│           └── logs/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                        # fixtures, including a fake LLM client
│   ├── fixtures/
│   │   └── papers/                        # at least 3 sample PDFs
│   ├── unit/
│   │   ├── test_schemas.py
│   │   ├── test_llm_client.py
│   │   ├── test_pdf_parser.py
│   │   └── test_<each_phase>.py
│   └── integration/
│       └── test_end_to_end.py
│
└── deploy/
    ├── huggingface_space/
    │   ├── app.py                         # Gradio UI (thin client — calls AMD VM)
    │   ├── README.md                      # Space metadata
    │   └── requirements.txt
    └── amd_vm/
        ├── start.sh                       # launches vLLM + GPU compute server
        ├── gpu_compute_server.py          # FastAPI: /bootstrap, /permutation, /robustness
        └── setup.md                       # one-time AMD VM setup instructions
```

### 4.1 `pyproject.toml` essentials

```toml
[project]
name = "research-repro"
version = "0.1.0"
requires-python = ">=3.11,<3.13"
dependencies = [
  "langgraph>=0.2",
  "pydantic>=2.6",
  "pydantic-settings>=2.2",
  "typer>=0.12",
  "httpx>=0.27",
  "openai>=1.30",            # used as OpenAI-compatible client for Ollama / vLLM
  "pymupdf>=1.24",
  "pdfplumber>=0.11",
  "beautifulsoup4>=4.12",
  "lxml>=5.0",
  "arxiv>=2.1",
  "tavily-python>=0.3",
  "datasets>=2.18",
  "kaggle>=1.6",
  "PyGithub>=2.3",
  "pandas>=2.2",
  "numpy>=1.26",
  "scipy>=1.13",
  "scikit-learn>=1.4",
  "matplotlib>=3.8",
  "seaborn>=0.13",
  "reportlab>=4.0",
  "mistune>=3.0",
  "python-dotenv>=1.0",
  "gradio>=4.0",
  "astroquery>=0.4",           # SDSS DR16 data access for target paper
  "instructor>=1.3",           # structured LLM output extraction with retry
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-asyncio>=0.23", "pytest-httpx>=0.30", "ruff>=0.4", "mypy>=1.10"]

[project.scripts]
repro = "research_repro.cli:app"
```

### 4.2 `.gitignore` additions

```
.env
.venv/
runs/
__pycache__/
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
deploy/huggingface_space/.cache/
```

---

## 5. Spec Updates Required Before Coding

Before any implementation, the agent updates these files **in this order** so docs and code land aligned:

1. **`llm-wiki/STACK.md`** — under "Core Reasoning → Language Model Inference":
   - Confirm single model: Qwen3.6-27B for all agent roles.
   - Add GPU compute layer: note that MI300X also runs PyTorch tensor workloads (bootstrap, permutation, robustness) alongside vLLM.
   - Add a row to the Decision Log: `2026-05-08 | Single model for all roles, deterministic Phase 6 comparisons | Simplicity; eval is primarily threshold math, not subjective LLM judgment`.

2. **`llm-wiki/ARCHITECTURE.md`** — under "Component 3: Agent Runtime" and the `config.json` example:
   - Update the config example to use single `model: {...}` block (not dual).
   - Add a "GPU Compute Layer" subsection noting the bootstrap/permutation/robustness endpoints.
   - Update the directory layout in §"Directory Layout (Code)" to use `src/research_repro/` (Python package layout) instead of bare `src/`.

3. **`llm-wiki/phase6_results_validation.md`** — add one paragraph at the start of "Comparison Methodology" noting that result comparisons use deterministic threshold-based classification (implemented in `tools/deterministic_comparison.py`), with the LLM used only for narrative generation and discrepancy attribution.

4. **Naming fix:** `llm-wiki/README.md` and `llm-wiki/ARCHITECTURE.md` reference `PROJECT_OVERVIEW.md`, but the file is `phase0_project_overview.md`. Update references to point to the actual filename. Do **not** rename the file.

These edits must be small and surgical. Do not reword unrelated content.

---

## 6. Build Sequence (Milestones)

**Build vertically.** Each milestone delivers a runnable slice. Do not start milestone N+1 until N's acceptance criteria pass.

### M1 — Foundations (infrastructure only)

**Goal:** the project loads, schemas validate, the LLM client is configured, and deterministic tools are ready.

**Tasks (in order):**

1. Bootstrap repo per §3.3 and §4.
2. Implement all schemas in `src/research_repro/schemas/` exactly per `llm-wiki/SCHEMAS.md`. Every model uses `ConfigDict(extra="forbid", strict=True)`. Add a `# Source: SCHEMAS.md §<section>` comment at the top of each file.
3. Implement `config.py` with `pydantic-settings`:
   - Reads `.env`
   - One `LLMEndpointConfig` object with `endpoint`, `model`, `api_key`, `temperature`, `max_tokens`.
   - `GPUComputeConfig` with `endpoint` (empty string = disabled; URL = call AMD VM).
   - Top-level `AppConfig` aggregates LLM config, GPU compute config, run defaults, concurrency limits, discrepancy thresholds.
4. Implement `tools/llm_client.py`:
   - Class `LLMClient` with one pre-bound `openai.OpenAI` client.
   - Method `chat(messages, response_model: type[BaseModel] | None) -> BaseModel | str`.
   - When `response_model` is given: include the JSON schema in the system prompt, set `response_format={"type": "json_object"}` if supported, parse and validate, retry up to 3× on `ValidationError`/`json.JSONDecodeError`.
   - Logs every call with token usage and latency.
5. Implement `tools/deterministic_comparison.py`:
   - Function `classify_comparison(reported, reproduced, thresholds) -> str` — returns match/close_match/moderate_discrepancy/significant_discrepancy based on relative error `abs(reported - reproduced) / max(abs(reported), 1e-9)`.
   - Function `statistical_comparison(reported_val, reproduced_ci) -> str` — returns `consistent` if `reported_val` ∈ `reproduced_ci`, else `inconsistent`. If comparing two p-values, checks if both cross the same $\alpha=0.05$ threshold.
   - No LLM calls. Pure arithmetic.
6. Implement `logging_setup.py` per the format in §2 rule 13.
7. Write `tests/unit/test_schemas.py` (instantiate every schema with minimal valid + invalid inputs, assert validation behavior).
8. Write `tests/unit/test_llm_client.py` with a fake OpenAI server (`pytest-httpx`) verifying retry logic and structured-output parsing.

**Acceptance:**
- `uv run pytest tests/unit -q` passes (using a fake `pytest-httpx` LLM client).
- **(Optional Smoke Test)** `python -c "from research_repro.tools.llm_client import LLMClient; from research_repro.config import AppConfig; c = LLMClient(AppConfig()); print(c.chat([{'role':'user','content':'reply with the JSON {\"ok\": true}'}]))"` returns `"ok"` (with Ollama running).

---

### M2 — Phase 1 + Orchestrator Skeleton + CLI

**Goal:** `repro https://arxiv.org/abs/2605.04781` runs Phase 1 end-to-end and writes a valid `phase1_output.json`.

**Tasks:**

1. **Paper ingestion tools:**
   - `tools/arxiv_fetcher.py`: given an arXiv URL or ID, return metadata + downloaded PDF path. Use the `arxiv` package.
   - `tools/pdf_parser.py`: extract structured text per page using PyMuPDF; return a `ParsedPaper` dataclass with `pages: list[str]`, `figures: list[FigureRef]`, `tables: list[TableRef]`, `metadata: dict`.
   - `tools/html_parser.py`: equivalent for arXiv abstract HTML pages.
   - Input router: a single function `ingest_paper(input_str) -> ParsedPaper` that detects arXiv link / PDF path / HTML URL and dispatches.

2. **Reader agent (`agents/reader.py`):**
   - `BaseAgent` in `agents/base.py` provides: `__init__(llm_client, role)`, `run_structured(prompt, response_model, source_text)` with built-in two-layer verification (§2 rule 14). Every extraction returns `(result, VerificationRecord)`.
   - `agents/verification.py` implements:
     - `deterministic_verify(result, source_text)` — Recursively traverses Pydantic models to find all `paper_quote` fields. For each, checks fuzzy match against `source_text` (`difflib.SequenceMatcher` ratio ≥ 0.8). If ratio < 0.8, flags for LLM coherence check. Also applies value-range assertions and completeness checks.
     - `coherence_verify(result, source_text_excerpt, llm_client)` — one lightweight LLM call that checks grounded/relevant/coherent. Used as a fallback for paraphrased claims or complex semantic verification.
   - Reader agent has methods that map 1:1 to Phase 1 sub-extractions:
     - `extract_metadata(parsed_paper) -> PaperMetadata`
     - `extract_summary(parsed_paper) -> PaperSummary`
     - `extract_datasets(parsed_paper) -> list[DatasetDescription]`
     - `extract_preprocessing_pipeline(parsed_paper) -> list[PreprocessingStep]`
     - `extract_methodology(parsed_paper) -> list[MethodSpecification]`
     - `extract_results(parsed_paper) -> list[ResultRecord]`
     - `extract_conclusions(parsed_paper) -> list[str]`
     - `detect_citation_dependencies(parsed_paper, methods) -> list[CitationDependency]`
     - `detect_ambiguity_flags(...) -> list[AmbiguityFlag]`
     - `assess_reproducibility_risk(artifact) -> str`
   - Each method calls `llm_client.chat(...)` with a prompt from `phases/phase1_paper_comprehension/prompts.py`.

3. **Phase 1 prompts (`phases/phase1_paper_comprehension/prompts.py`):**
   - One prompt template per Reader method, each instructing the model to:
     - Apply graduated attention per `phase1_paper_comprehension.md`.
     - Return JSON conforming to a specific schema (the schema's JSON Schema is injected into the prompt).
     - Include `paper_quote` and `location_in_paper` for every extracted item.
     - Flag ambiguities rather than guessing.

4. **Phase 1 executor (`phases/phase1_paper_comprehension/executor.py`):**
   - Function `run(input_path: str, run_dir: Path, config: AppConfig) -> PhaseResult`.
   - Sequence: ingest → metadata → summary → datasets → preprocessing → methodology → results → conclusions → citation deps → ambiguities → risk assessment.
   - Assembles `PaperKnowledgeArtifact`, validates, writes to `run_dir/phase1_output.json`.
   - Returns `PhaseResult(status, artifact_path, flags_raised)`.

5. **Orchestrator skeleton (`orchestrator.py`):**
   - LangGraph `StateGraph` with nodes for all six phases. Phases 2–6 are stubs that return `status="not_implemented"` and immediately route to a `partial_report` node.
   - Phase 1 node calls the Phase 1 executor, persists output, updates `PipelineState`.
   - Conditional edges: success → next phase; blocked → `partial_report`; not_implemented → `partial_report`.
   - Checkpointing via `MemorySaver` for now (`SqliteSaver` later when resumability is exercised).

6. **CLI (`cli.py`):**
   - Subcommands: `run <paper-input> [--mode auto|interactive] [--config path]`, `resume <run-dir>`, `inspect <run-dir>` (pretty-print phase outputs).
   - `run` creates `runs/run_<ts>_<slug>/`, writes `config.json`, invokes the orchestrator.

7. **Tests:**
   - Unit tests for each Reader method using a fake LLM that returns canned JSON.
   - One integration test: against a tiny fixture PDF (a 2-page synthetic paper checked into `tests/fixtures/papers/`), assert that `phase1_output.json` validates as `PaperKnowledgeArtifact`.

**Acceptance:**
- **CI Gate:** `uv run pytest tests/integration/test_phase1.py` passes using a local 2-page fixture PDF and a mocked LLM client, yielding a valid `phase1_output.json`.
- **Smoke Test:** `repro run https://arxiv.org/abs/2605.04781` completes without crashing (requires live Ollama and internet access).
- The produced `phase1_output.json` validates as `PaperKnowledgeArtifact` (load and `model_validate_json`).
- Manual review: at least the metadata (title, authors), the abstract, and one dataset / one method / one result are correctly extracted from the paper.
- `runs/.../artifacts/logs/phase1.log` contains LLM call records.

---

### M3 — Phase 2: Data Sourcing

**Goal:** Phase 2 takes the Phase 1 PKA, classifies each dataset (A–F), attempts download for A/B/C, flags D/E/F.

**Tasks:**

1. **Searcher agent (`agents/searcher.py`):** uses `tools/web_search.py` (Tavily), `tools/data_repos/*`, and `tools/http_fetch.py`. Methods:
   - `classify_dataset(dataset_description, paper_context) -> Category` (LLM call)
   - `search_repositories(query, hints) -> list[CandidateMatch]` (LLM-aided ranking after deterministic search)
   - `download_dataset(candidate) -> ProvenanceRecord` (deterministic — no LLM)
   - `validate_acquired_data(local_path, dataset_description) -> ValidationResult` (LLM compares schema/size/stats)

2. **`tools/data_repos/`:** one module per repository (Hugging Face, Kaggle, Zenodo, UCI scrape, OpenML, GitHub, Google Dataset Search via Tavily fallback). Each exposes `search(query) -> list[Hit]` and `download(hit, dest_dir) -> Path`.

3. **Phase 2 executor:** parallelizes per-dataset acquisition with `asyncio.gather` (concurrency limit from config). For each dataset:
   - Classify (A–F).
   - Route to acquisition strategy from `phase2_data_sourcing.md` §"Acquisition Strategy by Category".
   - Validate.
   - Build `DataAcquisitionRecord`.
   Assembles `DataManifest`, writes to `phase2_output.json`.

4. **Wire to orchestrator.** Replace the Phase 2 stub with the executor.

5. **Tests:** unit tests for each repo module (mock httpx responses); integration test using a fake PKA pointing to a Hugging Face dataset known to exist (e.g., `iris`).

**Acceptance:**
- For the target arXiv paper, Phase 2 produces a `DataManifest` whose `acquisitions` cover every dataset in the PKA.
- For Category A datasets, files exist on disk under `runs/.../artifacts/data/`.
- For Categories D/E/F, intervention flags are populated with the correct `flag_type`.

---

### M4 — Phase 3: Environment Reconstruction

**Goal:** Produce a working `environment.yml` and provision a conda env.

**Tasks:**

1. **`tools/conda_env.py`:** `create_env(yml_path, name) -> CondaEnv`, `verify_env(env, smoke_test_imports) -> bool`, `python_executable(env) -> Path`.
2. **Reader agent additions:** extend with methods for the five environment layers (language, deps, hardware, OS, reproducibility aids).
3. **Phase 3 executor:** extracts deps → uses `conda create --dry-run` to test dependency resolution, falling back to sequential pip installation if conda fails → writes `environment.yml` → calls `conda_env.create_env` → smoke tests imports → assembles `EnvironmentSpec`.
4. **Reproducibility target logic:** deterministic decision tree — if exact seeds + framework versions known → `numerical`; if seeds missing → `statistical`; if hardware mismatched too → `qualitative`.
5. **Wire to orchestrator.**

**Acceptance:** `phase3_output.json` validates; the conda env named in `EnvironmentSpec.conda_env_name` actually exists and `python -c "import <key_lib>"` succeeds inside it.

---

### M5 — Phase 4: Data Processing Replication

**Goal:** Generate, execute, and audit preprocessing code in the conda env from M4.

**Tasks:**

1. **Coder agent (`agents/coder.py`):** prompts the analysis LLM to write a single Python function per `PreprocessingStep`. Output is parsed as code blocks; functions are concatenated into one script per dataset.
2. **Executor agent (`agents/executor.py`):** wraps `tools/code_execution.py`. Runs the script in the conda env. **Security Sandbox:** Enforces strict timeouts (e.g., 15m), memory caps (via OS constraints), disables network access during execution if supported, restricts filesystem writes to a dedicated `runs/<run_id>/artifacts/sandbox/` dir, and limits imports. Captures stdout/stderr/exit/runtime into `ExecutionResult`. Wraps non-zero exits as `ExecutionFailure`.
3. **Validator agent (`agents/validator.py`):** compares before/after stats against the paper's data description, flags soft failures. Uses the same LLM.
4. **Phase 4 executor:** for each dataset → build pipeline script → execute → validate → on failure apply recovery protocol (try one alt interpretation, then mark unresolved). Assembles `ProcessedDatasetArtifact`.

**Acceptance:** `phase4_output.json` validates; processed dataset files exist; each step has a `PreprocessingExecutionRecord` with before/after shapes and stats.

---

### M6 — Phase 5: Analysis Execution

**Goal:** Implement and execute paper methods, capture results, handle multi-seed runs.

**Tasks:**

1. **Coder agent extensions:** generate analysis scripts per `MethodSpecification`. Hyperparameters become a top-level config dict.
2. **Executor agent extensions:** support multi-seed parallel runs (`ProcessPoolExecutor`, concurrency limit from config). Capture figures (matplotlib `savefig` to known paths).
3. **Failure recovery:** classify into Type 1–5 per `phase5_analysis_execution.md`. Up to 3 recovery attempts; then mark unresolved.
4. **Phase 5 executor:** smoke-test each method on a small subset before full run. Assembles `AnalysisResultsPackage`.

**Acceptance:** `phase5_output.json` validates; primary outputs and figures exist; for unseeded runs the package contains multi-seed statistics.

---

### M7 — Phase 6: Validation & Report

**Goal:** Compare reproduced vs reported using deterministic thresholds + LLM narrative, generate PDF + JSON report.

**Tasks:**

1. **Deterministic comparison (no LLM):**
   - Wire `tools/deterministic_comparison.py` (built in M1) into the Phase 6 executor.
   - For each `ResultRecord` from Phase 1, call `classify_comparison()` or `statistical_comparison()` against Phase 5 outputs.
   - Produces `ResultComparison` records with classifications.
2. **Validator agent extensions (same LLM):**
   - `attribute_discrepancy(comparison, all_phase_outputs) -> DiscrepancyAttribution` — LLM reviews audit logs to explain gaps.
   - `assess_claim(claim, comparisons) -> ClaimAssessment` — LLM assesses whether reproduced results support each conclusion.
3. **Reporter agent:** synthesizes the executive summary, recommendations, known gaps narrative.
4. **`tools/report_pdf.py`:** ReportLab template with the 9-section structure from `phase6_results_validation.md`.
5. **Phase 6 executor:** deterministic comparison (parallel) → discrepancy attribution (LLM) → claim assessment (LLM) → assemble `ReproducibilityReport` → render PDF → write JSON.
6. **Orchestrator end state:** Phase 6 success node → `END`. Update conditional edges so `partial_report` also calls Phase 6 in best-effort mode.

**Acceptance:** Running `repro run https://arxiv.org/abs/2605.04781` from scratch produces `final_report.pdf` and `final_report.json` whose `result_comparisons` cover every `ResultRecord` from Phase 1, with classifications and attributions populated.

---

### M8 — GPU Compute + Hugging Face Space Deployment

**Goal:** AMD MI300X runs bootstrap/permutation/robustness analysis; HF Space provides the frontend.

**Tasks:**

1. **`deploy/amd_vm/gpu_compute_server.py`:** FastAPI server with endpoints:
   - `POST /bootstrap` — batched bootstrap CIs using PyTorch on MI300X.
   - `POST /permutation` — permutation test for independent p-value verification.
   - `POST /robustness` — specification sweep (vary thresholds, quality cuts, line choices) and return robustness surface data.
   - Each endpoint accepts JSON arrays of data, returns JSON results.
2. **`deploy/amd_vm/requirements-gpu.txt`:** Dedicated dependencies for the AMD VM (`fastapi`, `uvicorn`, `torch`).
3. **`deploy/amd_vm/start.sh`:** single script that installs GPU deps, launches vLLM (port 8000) + GPU compute server (port 8001).
4. **`deploy/amd_vm/setup.md`:** one-time AMD VM setup: install ROCm, vLLM, clone repo, run `start.sh`.
5. **`tools/gpu_compute.py`:** client that calls the AMD VM endpoints. Falls back to CPU numpy equivalents when `AMD_COMPUTE_ENDPOINT` is empty (local dev).
5. **Wire GPU compute into Phase 5:** after replication code runs, call bootstrap CIs and permutation tests on the reproduced correlation values. Store results in `AnalysisResultsPackage`.
6. **`deploy/huggingface_space/app.py`:** Gradio interface — input box for arXiv URL / file upload, "Run" button, live log tail, downloads for the report PDF + JSON. Orchestrator runs directly in the Space process; LLM + GPU calls go to AMD VM.
7. **`deploy/huggingface_space/requirements.txt`:** mirror of `pyproject.toml` runtime deps.
8. **`deploy/huggingface_space/README.md`:** Space metadata header (title, sdk: gradio, etc.) + secret list (`LLM_ENDPOINT`, `AMD_COMPUTE_ENDPOINT`).
9. **End-to-end smoke test against the AMD VM** before submission.

**Acceptance:** the Space loads, accepts an arXiv URL, runs the full pipeline using the AMD VM for LLM + GPU compute, and surfaces the report for download. GPU compute endpoints return bootstrap CIs and robustness surface data.

---

## 7. Cross-Cutting Concerns

### 7.1 Logging
- One `logging.Logger` per module, named `research_repro.<module>`.
- Per-phase file handler attached at phase start, detached at phase end.
- DEBUG level captures full prompts/responses; INFO level captures call summaries.
- Pipeline-level handler writes to `runs/.../artifacts/logs/pipeline.log`.

### 7.2 Error handling
- LLM call failures: 3 retries with exponential backoff in `LLMClient`.
- Schema validation failures inside an agent: same — retry with the validation error embedded in a follow-up prompt asking the model to fix.
- Subprocess failures: captured as `ExecutionFailure`, classified per the relevant phase doc, never raised.
- Phase-level failures: returned as `PhaseResult(status="blocked", ...)`. Orchestrator decides routing.
- Top-level orchestrator exceptions: caught, written to `pipeline_state.json` with `overall_status="terminated"`, partial report attempted.

### 7.3 Testing strategy
- **Unit tests** per module, mocking external services (LLM, web). Coverage target: every agent method, every tool function.
- **Fixture papers:** at minimum (a) one ML paper with code+data on GitHub (easy mode), (b) one statistical/social-science paper with public CSV data (medium), (c) the target arXiv paper (full).
- **Integration test:** run full pipeline against the easiest fixture; assert all six artifacts validate and the report PDF exists.
- **Smoke test pre-deploy:** full run against the target paper using the AMD VM endpoint.

### 7.4 Secrets handling
- `.env` only. Never log secret values. `pydantic-settings` loads them; `repr` of the config redacts API keys.
- HF Space secrets configured via the Space settings UI, not committed.

### 7.5 Resumability
- After M2, the orchestrator can resume from any persisted phase output. Implementation: `cli resume <run-dir>` reads `pipeline_state.json`, identifies last completed phase, re-enters the StateGraph at the next node.

### 7.6 Idempotency
- Re-running a phase with the same inputs must produce the same output (modulo LLM nondeterminism, which is bounded by `temperature=0.0`).
- Phase outputs are written atomically (write to `*.tmp`, then `os.replace`).

---

## 8. Definition of Done

**Offline CI Gate (Required for codebase merge):**
1. `uv run pytest -q` passes all unit and integration tests using mocked external services and local fixture data.
2. Every phase output JSON validates against its Pydantic schema on cold reload.
3. Spec edits from §5 are committed and `llm-wiki/` reflects the single-model + GPU compute architecture.

**End-to-End Demo Gate (Required for hackathon submission):**
4. `repro run https://arxiv.org/abs/2605.04781` completes Phases 1–6 (with Ollama or AMD VM) and produces `final_report.pdf` and `final_report.json`.
5. The Hugging Face Space at `deploy/huggingface_space/` accepts an arXiv URL via Gradio, runs the full pipeline using AMD VM for LLM + GPU compute, and offers the report for download.
6. The final report identifies, for at least the target paper:
   - The reproducibility target chosen.
   - At least one ambiguity flag with assumption documented.
   - A claim-level assessment.
   - Bootstrap confidence intervals on reproduced correlation values (via GPU compute).

---

## 9. Gotchas & Common Pitfalls

| Pitfall | Mitigation |
|---|---|
| Ollama returns plain text instead of JSON | Use `format: "json"` parameter (Ollama-specific) **only as a backstop**; primary path is prompt-engineered JSON + retry-on-parse-fail. Do not rely on the param being honored when swapping to vLLM. |
| Conda env activation on Windows | Use `conda run -n <env> python script.py` rather than activating in the parent shell. Cross-platform. |
| PyMuPDF column-order issues on two-column papers | Fall back to `pdfplumber` when extracted text contains words like "abstract" or "introduction" that appear out of order. |
| arXiv 2605.04781 is from May 2026 (very recent) | If the `arxiv` package can't resolve it, fetch the PDF directly from `https://arxiv.org/pdf/2605.04781` and parse without metadata; surface the metadata gap as an `AmbiguityFlag`. |
| LangGraph state object size | Don't store entire artifacts in `PipelineState`; only paths. Schemas already enforce this. |
| AMD VM endpoint not publicly reachable from HF Spaces | Use Cloudflare Tunnel (free) or ngrok. Document in `deploy/amd_vm/setup.md`. |
| Phase 5 GPU compute and vLLM sharing MI300X | Don't run GPU compute concurrently with LLM inference. Phase 5 compute happens after LLM-generated code is written. Alternatively use `torch.cuda.set_per_process_memory_fraction(0.4)` for compute jobs. |
| vLLM open on public IP without auth | Acceptable for hackathon (50hr credits, temporary VM). Do not commit the IP to git — keep as HF Space secret. |
| Token-limit failures on long papers | Chunk by section in the Reader agent. Each Phase 1 sub-extraction operates on the relevant section, not the whole paper. |
| Schema drift mid-build | Single source of truth is `src/research_repro/schemas/`. If the agent finds itself wanting to "match" the markdown over the Python, stop and update both per the protocol in `SCHEMAS.md` §"Schema Evolution". |
| GPU compute fallback in local dev | `tools/gpu_compute.py` must have CPU numpy fallbacks for bootstrap/permutation when `AMD_COMPUTE_ENDPOINT` is empty. Local dev works without AMD VM. |
| HF Space timeout (free tier) | Free Spaces have a 72-hour inactivity timeout and limited CPU/RAM. For the demo, keep the Space running during judging. Full pipeline on a long paper may exceed memory — test beforehand. |
| `uv init` on existing repo | The repo already has files. Use `uv init --package research-repro --no-readme` to avoid overwriting existing content. If `pyproject.toml` already exists, edit it manually instead. |
| Qwen 3.5 "thinking" tokens break structured output | Qwen 3.5 models on Ollama emit reasoning in a `thinking` field and leave `content` empty. This crashes JSON parsing and `instructor`. **Mitigation:** In `LLMClient`, if `response.choices[0].message.content` is empty/null, check `response.choices[0].message.model_extra` for a `thinking` field and extract content from there. Alternatively, pass `think=False` or equivalent parameter if the model supports it. Test this during M1 acceptance. |
| `asyncio.gather` in a sync codebase | M3 Phase 2 executor uses `asyncio.gather` but the rest of the codebase (typer CLI, subprocess calls) is synchronous. Use `concurrent.futures.ThreadPoolExecutor` instead — it integrates cleanly with the sync codebase and avoids wrapping everything in `asyncio.run()`. |
| Prefer arXiv HTML over PDF for text extraction | The target paper has an experimental HTML version (`https://arxiv.org/html/2605.04781v1`) with proper section structure, no column-order issues, and clean math rendering. In `ingest_paper()`, try the HTML version first for arXiv papers, fall back to PDF only if HTML is unavailable. This significantly improves Phase 1 extraction quality. |

---

## 10. Order of Operations Summary

1. Read all of §1.
2. Apply §5 spec updates (small, ~30 minutes).
3. Run §3 setup once.
4. Build M1 → verify acceptance.
5. Build M2 → verify acceptance against the target arXiv paper. **Stop here and request human review** — the Phase 1 output is the highest-leverage artifact; getting it wrong cascades.
6. Build M3 → M7 in order, verifying each milestone's acceptance criteria before proceeding.
7. Build M8 only after the user confirms the AMD VM is provisioned and reachable.
8. Run §8's full Definition of Done checklist before declaring complete.

When unsure about scope, defer to the relevant phase doc in `llm-wiki/`. When the phase doc and `SCHEMAS.md` disagree, follow the schema and flag the inconsistency.
