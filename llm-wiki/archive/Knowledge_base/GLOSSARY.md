# Glossary

## Purpose

This document defines every domain-specific term used in the project. When a coding agent encounters a term in any document or code file, this glossary is the authoritative reference for what it means. Terms are alphabetized within each section for quick lookup.

---

## Naming Conventions

Before the term definitions, here are the conventions every agent must follow:

- **Class names:** `PascalCase` — e.g., `PaperKnowledgeArtifact`, `CitationDependency`
- **Variable and function names:** `snake_case` — e.g., `paper_artifact`, `extract_preprocessing_steps()`
- **File names:** `snake_case.py` for code, `UPPER_CASE.md` for top-level docs (PROJECT_OVERVIEW, ARCHITECTURE, etc.), `lower_case.md` for phase docs
- **JSON field names:** `snake_case` — e.g., `"paper_quote"`, `"location_in_paper"`
- **Constants:** `UPPER_SNAKE_CASE` — e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT_SECONDS`
- **Acronyms in prose:** uppercase when standalone (e.g., "the PKA contains..."), but in code referenced by full PascalCase class name (`PaperKnowledgeArtifact`), never as `PKA` in class names

---

## Project-Level Terms

### Autonomous Research Reproducibility Engine
The full system described in this project. The complete six-phase pipeline plus orchestrator. Often shortened in prose to "the engine" or "the system."

### Phase
One of six sequential stages in the pipeline. Phases are numbered 1 through 6 and have fixed responsibilities defined in their respective methodology documents (`phase1_*.md` through `phase6_*.md`).

### Phase Methodology Document
A markdown file (`phase1_paper_comprehension.md`, etc.) defining what a phase does conceptually. These are the human-reviewer-voice specifications. They define behavior, not implementation.

### Pipeline
The full sequence of all six phases executed in order. Synonymous with "the engine" in conversational use.

### Run
A single execution of the pipeline against a single input paper. Each run has its own directory under `runs/`.

### Run Directory
The filesystem location containing all artifacts and logs for a single run. Format: `runs/run_{timestamp}_{paper_slug}/`.

### Reproducibility Target
The level of agreement between original and reproduced results that the pipeline aims for, given the available environment information. One of: `exact`, `numerical`, `statistical`, `qualitative`. Determined by Phase 3 and used by Phase 6 as the comparison standard.

---

## Phase-Specific Artifacts

### Paper Knowledge Artifact (PKA)
The structured output of Phase 1. Contains all extracted information from the paper: metadata, summary, datasets, preprocessing pipeline, methodology, results, conclusions, citation dependencies, and ambiguity flags. Implemented as the `PaperKnowledgeArtifact` Pydantic model. The single source of truth for everything the system knows about the paper.

### Data Manifest
The structured output of Phase 2. Contains the acquisition status, local paths, and validation results for each dataset described in the PKA. Implemented as the `DataManifest` Pydantic model.

### Environment Specification Package
The structured output of Phase 3. Contains the dependency manifest, environment files (`environment.yml`, `requirements.txt`), assumptions, hardware gaps, and the reproducibility target. Implemented as the `EnvironmentSpec` Pydantic model. Often shortened to "environment spec."

### Processed Dataset Artifact
The structured output of Phase 4. Contains the paths to processed datasets, the assembled preprocessing code, execution records for each preprocessing step, and the replicability assessment. Implemented as the `ProcessedDatasetArtifact` Pydantic model.

### Analysis Results Package
The structured output of Phase 5. Contains the execution records for each method, primary outputs, multi-seed run results, sensitivity analyses, and any failures. Implemented as the `AnalysisResultsPackage` Pydantic model.

### Reproducibility Report
The structured output of Phase 6 and the final deliverable of the pipeline. Contains the executive summary, overall score, result comparisons, discrepancy attributions, claim assessments, and recommendations. Produced in both JSON (machine-readable) and PDF (human-readable) form. Implemented as the `ReproducibilityReport` Pydantic model.

### Pipeline State
The global state object tracked by the LangGraph orchestrator. Records which phases have completed, paths to all phase outputs, mode, and overall status. Implemented as the `PipelineState` Pydantic model.

---

## Records and Flags

These are sub-structures that appear within multiple phase outputs.

### Citation Backstop
The mechanism by which the system halts extraction or implementation when a method, dataset, or step is referenced by citation only and not described in the paper. Triggered in Phase 1 (during extraction) and again in Phase 5 (during implementation if the citation was not resolved). Produces a `CitationDependency` record.

### Citation Dependency
A record produced by the Citation Backstop. Identifies what was cited, where, and what its impact on reproducibility is. Implemented as the `CitationDependency` Pydantic model.

### Ambiguity Flag
A record produced when a detail in the paper is underspecified. Categorized by type (e.g., `data_ambiguity`, `hyperparameter_gap`, `metric_ambiguity`). Implemented as the `AmbiguityFlag` Pydantic model.

### Execution Failure
A record produced when generated code fails to execute. Categorized by failure type (`environment`, `data`, `implementation`, `convergence`, `resource`, `hard`, `soft`). Implemented as the `ExecutionFailure` Pydantic model.

### Human Intervention Flag
A record raised when human input is required to proceed. Categorized by type (e.g., `restricted_data`, `data_access_failure`, `missing_random_seed`). Has a `blocking` boolean indicating whether the pipeline can continue without resolution. Implemented as the `HumanInterventionFlag` Pydantic model.

### Provenance Record
A record tracking the origin of any acquired artifact (typically a dataset). Includes source URL, access method, download timestamp, and file hash. Implemented as the `ProvenanceRecord` Pydantic model.

### Hardware Gap Record
A record describing a discrepancy between the hardware the paper used and the hardware available for replication. Implemented as the `HardwareGap` Pydantic model.

### Environment Assumption
A record documenting an inference made during environment reconstruction (e.g., inferring a library version from the publication date). Implemented as the `EnvironmentAssumption` Pydantic model.

### Preprocessing Assumption Record
An `AmbiguityFlag` of type `preprocessing_ambiguity` raised during Phase 4 when an ambiguous preprocessing step had to be resolved with an assumption.

### Hyperparameter Default Record
A record produced in Phase 5 when a hyperparameter not specified in the paper was set to a library default. Stored within `MethodExecutionRecord.hyperparameter_defaults`.

### Metric Ambiguity Record
An `AmbiguityFlag` of type `metric_ambiguity` raised when a metric definition in the paper is unclear and a convention had to be chosen.

### Result Record
A single result extracted from the paper in Phase 1. Has a unique `result_id` referenced throughout downstream phases. Implemented as the `ResultRecord` Pydantic model.

### Result Comparison
A single comparison between a paper's reported result and the reproduced equivalent, produced in Phase 6. Implemented as the `ResultComparison` Pydantic model.

### Discrepancy Attribution
The analysis explaining why a particular result did not match exactly, produced in Phase 6. Classifies the discrepancy as `explained`, `partially_explained`, or `unexplained`. Implemented as the `DiscrepancyAttribution` Pydantic model.

### Claim Assessment
The evaluation of whether the reproduced results support a specific claim from the paper's conclusion, produced in Phase 6. Implemented as the `ClaimAssessment` Pydantic model.

---

## Architecture Terms

### Orchestrator
The top-level controller that executes phases in sequence and manages state. Implemented as a LangGraph `StateGraph` in `src/orchestrator.py`.

### Phase Executor
The module implementing a single phase. Located at `src/phases/phase{N}_*/executor.py`. Receives input artifacts, runs internal agents, and produces an output artifact.

### Agent
A function within a phase that calls the LLM (via vLLM) to perform a specific reasoning task. Categorized by role: Reader, Searcher, Coder, Executor, Validator, Reporter.

### Tool
A deterministic capability exposed to agents (web search, file I/O, code execution, schema validation, etc.). Located in `src/tools/`.

### Mode
The operational mode of a run. One of:
- `auto` — flags are recorded but the pipeline continues; default for hackathon demos
- `interactive` — flags pause the pipeline and wait for user input

### Reader Agent / Searcher Agent / Coder Agent / Executor Agent / Validator Agent / Reporter Agent
The six categories of agents by role. Their responsibilities are defined in `ARCHITECTURE.md`.

### Conda Environment
The isolated Python environment provisioned by Phase 3 for executing replicated code. Named `repro_run_{timestamp}`. Defined by an `environment.yml` file.

### Subprocess Execution
The mechanism for running generated code: a fresh Python subprocess invoked via `subprocess.run`, using the conda environment's Python interpreter, with timeout and resource limits.

---

## Classification Vocabularies

### Result Comparison Classifications (Phase 6)

- **match** — within floating-point tolerance (relative error < 1e-6)
- **close_match** — small but outside tolerance (relative error < 1%)
- **moderate_discrepancy** — relative error between 1% and 10%
- **significant_discrepancy** — relative error > 10%
- **statistically_consistent** — paper value within reproduced distribution (multi-seed runs)
- **borderline** — paper value at edge of reproduced distribution
- **statistically_inconsistent** — paper value outside reproduced distribution
- **qualitative_match** — same direction and ordering, magnitudes differ
- **qualitative_mismatch** — different direction or ordering
- **not_reproduced** — replication could not produce a comparable value

### Phase Status Values

- **pending** — phase has not started
- **in_progress** — phase is currently executing
- **complete** — phase finished successfully with no flags
- **partial** — phase finished but with one or more non-blocking flags
- **blocked** — phase cannot proceed without human intervention
- **failed** — phase encountered an unrecoverable error

### Overall Reproducibility Score (Phase 6)

- **high** — all primary results reproduced within target; all discrepancies explained
- **moderate** — most results reproduced; some unexplained discrepancies but core claims supported
- **low** — significant results not reproduced; some core claims not supported
- **failed** — blocking failures prevented meaningful comparison

### Data Source Categories (Phase 2)

- **Category A** (`A_public_specified`) — fully specified public dataset
- **Category B** (`B_public_partial`) — partially specified public dataset
- **Category C** (`C_author_provided`) — author-provided via supplementary materials or repo
- **Category D** (`D_proprietary`) — proprietary or restricted access
- **Category E** (`E_custom_generated`) — custom-generated by the authors
- **Category F** (`F_unspecified`) — source unknown

---

## Conventions for Cross-References

When referring to other documents in code comments or prose:

- Phase docs: cite by number — "see Phase 4" or "per `phase4_data_processing.md`"
- Architecture: "see `ARCHITECTURE.md`"
- Schemas: "see `SCHEMAS.md`" or by class name when the class is the focus — "the `PaperKnowledgeArtifact` schema"
- Stack choices: "see `STACK.md`"
- This glossary: "see `GLOSSARY.md`"

When introducing a glossary term in prose for the first time in a document, add a parenthetical pointer if the term is non-obvious: "...the Citation Backstop (see `GLOSSARY.md`) is triggered..."

---

## When To Update This Document

- A new term is introduced in any phase doc, architecture doc, or schema
- A term's meaning is refined or scoped differently
- A new classification vocabulary is added
- A new artifact type is introduced

The glossary is the slowest-moving of the four operational docs (`ARCHITECTURE`, `STACK`, `SCHEMAS`, `GLOSSARY`). When a term changes, all four docs and the affected phase docs should be reviewed for consistency.
