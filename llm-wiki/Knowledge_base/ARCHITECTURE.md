# System Architecture

## Purpose

This document defines the runtime architecture of the Autonomous Research Reproducibility Engine. The phase methodology documents (`phase1_*.md` through `phase6_*.md`) define what each phase must accomplish. This document defines how those phases are executed, orchestrated, and recovered. Together with `STACK.md`, `SCHEMAS.md`, and `GLOSSARY.md`, this forms the operational contract for the system.

---

## Architectural Overview

The system is a sequential, stateful, checkpoint-based pipeline. Six phases execute in order, each consuming the output artifact of the previous phase and producing its own. A global orchestrator manages phase transitions, persistence, error handling, and human-in-the-loop pauses.

Within each phase, one or more agents collaborate to produce the phase's output artifact. Agents within a phase may execute in parallel when the work is independent (e.g., sourcing multiple datasets in Phase 2). Agents across phases never run concurrently.

The system is built on LangGraph, which provides the state graph abstraction and native checkpointing. All inter-phase data flow uses Pydantic models defined in `SCHEMAS.md` for strict validation and serialization.

---

## Top-Level Components

### Component 1: Orchestrator

The orchestrator is the top-level controller. Its responsibilities:

- Initialize the pipeline with the user's input (paper URL or file path) and configuration
- Execute each phase in sequence
- Persist phase outputs to disk after each phase completes
- Detect failures and route them through the recovery protocol
- Pause the pipeline when human intervention is required (in interactive mode) or skip and flag (in auto mode)
- Produce the final report at the end of Phase 6

The orchestrator is implemented as a LangGraph `StateGraph` where each node corresponds to a phase. Edges between nodes are conditional, based on the state of the previous phase's output (success, partial success, blocked).

### Component 2: Phase Executors

Each phase is implemented as a self-contained module under `phases/phase{N}_{name}/`. A phase executor:

- Loads its input artifact from the state store
- Validates the input against the relevant Pydantic schema
- Runs its internal agent(s) to produce the output artifact
- Validates the output against its schema
- Saves the output artifact to the state store
- Returns a `PhaseResult` to the orchestrator (status, artifact path, flags raised)

Phase executors do not know about each other. They communicate only through artifacts persisted by the orchestrator.

### Component 3: Agent Runtime

Within a phase, work is performed by one or more agents. Each agent is a function that takes structured input, calls the LLM (via vLLM), optionally invokes tools, and returns structured output validated against a Pydantic model.

Agents are categorized by role:

- **Reader agents** — extract information from text (papers, web pages, code files)
- **Searcher agents** — interact with external sources (web search, dataset repositories, GitHub)
- **Coder agents** — write Python code based on structured specifications
- **Executor agents** — invoke the code execution layer to run code and capture outputs
- **Validator agents** — compare outputs against expectations and produce structured assessments
- **Reporter agents** — synthesize structured artifacts into human-readable form

A single phase may use multiple agent roles. Phase 1 uses primarily Reader agents. Phase 4 uses Coder, Executor, and Validator agents in tight collaboration.

### Component 4: Tool Layer

Tools are deterministic capabilities exposed to agents. Tools include:

- Web search (for dataset discovery, citation following)
- File system operations (read paper, download data, save artifacts)
- HTTP fetch (download datasets from URLs)
- Code execution (run Python directly on the VM with isolation per phase)
- Schema validation (verify output conforms to expected Pydantic model)
- Inference call to vLLM (for sub-agent reasoning calls)

Tools are stateless and side-effect-aware. Every tool call is logged with input, output, and timestamp.

### Component 5: State Store

All pipeline state is persisted to disk under a single run directory:

```
runs/
  run_{timestamp}_{paper_slug}/
    config.json                 # run configuration
    pipeline_state.json         # global pipeline state
    phase1_output.json          # PaperKnowledgeArtifact
    phase2_output.json          # DataManifest
    phase3_output.json          # EnvironmentSpec
    phase4_output.json          # ProcessedDatasetArtifact
    phase5_output.json          # AnalysisResultsPackage
    phase6_output.json          # ReproducibilityReport
    artifacts/
      data/                     # raw and processed datasets
      code/                     # generated code files
      figures/                  # reproduced visualizations
      logs/                     # per-phase execution logs
    final_report.pdf            # human-readable report
    final_report.json           # machine-readable report
```

Each phase output is a JSON file conforming to the Pydantic schema defined in `SCHEMAS.md`. The `pipeline_state.json` tracks which phases have completed, which are in progress, which raised flags, and the overall status.

---

## Code Execution Model

Code generated by Phase 4 and Phase 5 executes directly on the VM, not in a container. Isolation is achieved through:

- **Per-phase working directories:** Each phase has a dedicated working directory under `artifacts/code/phase{N}/`. Generated code is written here and executed with this directory as the working directory.
- **Process-level execution:** Each code execution is a fresh Python subprocess invoked via `subprocess.run`, with timeout limits and captured stdout/stderr. The subprocess inherits the conda environment provisioned in Phase 3 but does not share state with the orchestrator process.
- **Resource limits:** Subprocesses are launched with explicit memory and time limits. Default time limit is 30 minutes per execution; can be overridden in config for long-running training jobs.
- **Filesystem boundaries:** Generated code is allowed to read from `artifacts/data/` (raw data) and write to its own working directory. Writes outside the working directory are not enforced at the OS level but are flagged in code review by the Coder agent before execution.
- **Error capture:** All execution failures (non-zero exit, timeout, OOM) are captured as structured `ExecutionFailure` records with stdout, stderr, exit code, and runtime metrics.

The system trusts the code it generates. Hardening (containerization, restricted Python, etc.) can be added later but is not part of the hackathon scope.

---

## Concurrency Model

### Across phases
Phases execute strictly sequentially. The orchestrator does not start phase N+1 until phase N has completed and its output artifact is validated and persisted.

### Within a phase
Agents within a phase may execute in parallel when the work units are independent. Specifically:

- **Phase 2:** Multiple datasets are sourced in parallel. Each dataset's acquisition is an independent task with its own searcher agent.
- **Phase 5:** Multiple seed runs (when reproducibility target is statistical) are executed in parallel up to a configured concurrency limit.
- **Phase 6:** Per-result comparisons are independent and may run in parallel.

All other phases are sequential within themselves.

Parallelism is implemented via Python's `asyncio` for I/O-bound work (web search, downloads) and `concurrent.futures.ProcessPoolExecutor` for CPU/GPU-bound work (model training in Phase 5). The concurrency limit defaults to 4 and is configurable.

---

## Failure Handling and Recovery

### Failure classification
Failures are classified by the phase that produced them, using the classifications defined in the relevant phase document. The orchestrator does not redefine failure types; it routes them.

### Recovery levels

**Level 1 — Within-agent retry:** An agent encountering a transient failure (network error, malformed LLM output) retries up to 3 times with exponential backoff. This is handled inside the agent and not surfaced to the orchestrator.

**Level 2 — Phase-internal recovery:** A phase encountering a recoverable failure (e.g., one of three datasets fails to download, but the others succeed) marks the failed unit, continues with the rest, and produces a partial output artifact with the failure recorded. The orchestrator sees this as a "partial success" and decides whether to continue.

**Level 3 — Pipeline-level decision:** A phase that cannot produce a meaningful output (e.g., paper extraction completely fails, no datasets accessible) returns a "blocked" status. The orchestrator either pauses for human input (interactive mode) or terminates the pipeline with a partial report (auto mode).

### Resumability
Every phase output is persisted on completion. If the pipeline is interrupted (crash, manual stop, system reboot), it can be resumed by re-invoking the orchestrator with the same run directory. The orchestrator detects the latest completed phase from `pipeline_state.json` and resumes from the next phase.

A phase that was interrupted mid-execution is restarted from the beginning of that phase. Within-phase checkpointing is not implemented in v1. Phases are designed to be idempotent — re-running a phase produces the same output given the same input.

---

## Human-in-the-Loop

Two modes are supported, set via config:

### Auto mode (default for hackathon demo)
When a phase raises a flag requiring human intervention, the system:
- Records the flag in the phase output and `pipeline_state.json`
- Skips the affected work unit (e.g., the inaccessible dataset)
- Continues with the rest of the pipeline
- Surfaces all flags prominently in the final report

### Interactive mode
When a flag is raised, the system:
- Pauses the pipeline
- Writes a `human_input_required.json` file to the run directory describing the flag and what input is needed
- Waits for the user to either provide the input (e.g., manually downloaded data placed in a specified location) or to mark the flag as "skip"
- Resumes from the same phase with the new state

Interactive mode uses a simple file-watcher polling pattern. No web UI in v1.

---

## Configuration

A single `config.json` file controls all run-level settings:

```json
{
  "paper_input": "https://arxiv.org/abs/...",
  "run_directory": "runs/run_20260507_143022_paper-slug",
  "mode": "auto",
  "model": {
    "name": "Qwen3.6-32B",
    "vllm_endpoint": "http://localhost:8000/v1",
    "max_tokens": 4096,
    "temperature": 0.0
  },
  "execution": {
    "subprocess_timeout_seconds": 1800,
    "max_memory_gb": 32
  },
  "concurrency": {
    "phase2_max_parallel_downloads": 4,
    "phase5_max_parallel_seeds": 3
  },
  "flags": {
    "max_seed_runs_when_unseeded": 5,
    "discrepancy_thresholds": {
      "match": 1e-6,
      "close_match": 0.01,
      "moderate": 0.10
    }
  }
}
```

Defaults are provided for all fields. The user only needs to specify `paper_input`.

---

## Logging and Observability

Every phase produces a per-phase log file under `artifacts/logs/phase{N}.log`. Logs include:

- Timestamp of every agent invocation
- Tool calls with inputs and outputs
- LLM calls with token counts (full prompts/responses logged at DEBUG level only)
- All failures with full stack traces
- All flags raised

A global `pipeline.log` aggregates phase-level events for high-level observability.

Logs are plain text in standard Python logging format. No external logging service in v1.

---

## Directory Layout (Code)

```
research-reproducibility-engine/
  PROJECT_OVERVIEW.md
  ARCHITECTURE.md
  STACK.md
  SCHEMAS.md
  GLOSSARY.md
  phase1_paper_comprehension.md
  phase2_data_sourcing.md
  phase3_environment_reconstruction.md
  phase4_data_processing.md
  phase5_analysis_execution.md
  phase6_results_validation.md
  
  src/
    orchestrator.py          # LangGraph StateGraph
    config.py                # Pydantic config models
    schemas/                 # all Pydantic schemas
      __init__.py
      paper_knowledge.py
      data_manifest.py
      environment_spec.py
      processed_dataset.py
      analysis_results.py
      reproducibility_report.py
      common.py              # shared records (CitationDependency, etc.)
    
    agents/
      base.py                # base agent abstraction
      reader.py
      searcher.py
      coder.py
      executor.py
      validator.py
      reporter.py
    
    tools/
      web_search.py
      http_fetch.py
      code_execution.py
      pdf_parser.py
      vllm_client.py
    
    phases/
      phase1_paper_comprehension/
        executor.py          # phase entry point
        prompts.py           # all LLM prompts for this phase
      phase2_data_sourcing/
        executor.py
        prompts.py
      phase3_environment_reconstruction/
        executor.py
        prompts.py
      phase4_data_processing/
        executor.py
        prompts.py
      phase5_analysis_execution/
        executor.py
        prompts.py
      phase6_results_validation/
        executor.py
        prompts.py
        report_generator.py  # PDF rendering
    
    cli.py                   # command-line entry point
  
  runs/                      # generated run directories (gitignored)
  
  tests/
    fixtures/                # sample papers for testing
    test_phase1.py
    ...
  
  pyproject.toml
  README.md
```

---

## How LangGraph Wires the Pipeline

At a high level, the orchestrator constructs a `StateGraph` whose state is a single `PipelineState` Pydantic model containing references to all phase outputs. Each phase is a node:

```
START
  -> phase1_node
  -> phase2_node
  -> phase3_node
  -> phase4_node
  -> phase5_node
  -> phase6_node
  -> END
```

Each node:
1. Reads the relevant inputs from `PipelineState`
2. Invokes the phase executor
3. Writes the phase output to disk
4. Updates `PipelineState` with the path to the new output
5. Returns the updated state

Conditional edges check the phase result status. If a phase returns "blocked" and mode is "auto", the graph routes to a `partial_report` node and ends. If mode is "interactive", it routes to a `wait_for_input` node.

Checkpointing is enabled via LangGraph's `MemorySaver` or `SqliteSaver`, persisting the full state graph after each node transition.

---

## What Is Out of Scope for v1

- Distributed execution across multiple VMs
- Web-based UI
- Real-time monitoring dashboard
- Multi-user concurrent runs
- Persistent caching of dataset downloads across runs
- Automatic Citation Backstop resolution (following citations to other papers)

These are deliberate omissions to keep the hackathon scope tight. Each can be added in a v2 without changing the phase-level architecture.
