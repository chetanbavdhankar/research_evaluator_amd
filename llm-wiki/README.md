# Autonomous Research Reproducibility Engine — Documentation

This folder contains the complete specification for the Autonomous Research Reproducibility Engine: a multi-agent system that takes a research paper as input and autonomously attempts to reproduce its results.

The documents are organized as a layered LLM wiki. They are designed to be read by both human collaborators and coding agents. Read them in the order suggested below.

---

## Reading Order

### 1. Start here
**`phase0_project_overview.md`** — the philosophy, motivation, and high-level idea. Read this first to understand what the project is and why it exists. Do not skip it; everything else assumes this context.

### 2. Operational layer
Read these next, in order. Together they define how the system is built and how it behaves at runtime.

- **`ARCHITECTURE.md`** — runtime architecture: orchestrator, phase executors, agent runtime, tool layer, state store, code execution model, concurrency, failure handling, resumability, human-in-the-loop modes, directory layout
- **`STACK.md`** — locked technology choices for every layer (vLLM, LangGraph, Pydantic, conda, etc.) with rationale
- **`SCHEMAS.md`** — Pydantic models for every inter-phase artifact and shared record types; the formal contract between phases
- **`GLOSSARY.md`** — naming conventions and definitions of every domain term used across the project

### 3. Phase methodology layer
Read these in numerical order. Each defines what one phase of the pipeline must accomplish, written from a thorough-human-reviewer perspective.

- **`phase1_paper_comprehension.md`** — extract structured knowledge from the paper
- **`phase2_data_sourcing.md`** — locate and acquire the datasets used
- **`phase3_environment_reconstruction.md`** — identify and provision the computational environment
- **`phase4_data_processing.md`** — replicate every preprocessing step
- **`phase5_analysis_execution.md`** — implement and run the analytical methods
- **`phase6_results_validation.md`** — compare reproduced outputs to the paper and produce the final report

---

## How These Documents Relate

```
phase0_project_overview.md
        |
        |  (defines the why)
        v
+----------------------------------+
| ARCHITECTURE.md   STACK.md       |
| SCHEMAS.md        GLOSSARY.md    |   (define the how)
+----------------------------------+
        |
        |  (operational contract for)
        v
phase1 -> phase2 -> phase3 -> phase4 -> phase5 -> phase6
                  (define the what, per stage)
```

- `phase0_project_overview.md` is the entry point and context anchor
- The four operational docs (`ARCHITECTURE`, `STACK`, `SCHEMAS`, `GLOSSARY`) are the cross-cutting reference layer; any phase can rely on them
- The six phase docs are sequential and reference each other through the artifacts they produce and consume

---

## Documents at a Glance

| File | Purpose | Length | When to read |
|------|---------|--------|--------------|
| `phase0_project_overview.md` | Why the project exists | ~5 min | First |
| `ARCHITECTURE.md` | How the runtime works | ~10 min | Before writing any code |
| `STACK.md` | Which tools are used | ~5 min | When choosing a library |
| `SCHEMAS.md` | Data contracts between phases | ~10 min | When implementing a phase |
| `GLOSSARY.md` | Terminology and conventions | ~5 min | Reference, anytime |
| `phase1_paper_comprehension.md` | Phase 1 methodology | ~10 min | Before building Phase 1 |
| `phase2_data_sourcing.md` | Phase 2 methodology | ~10 min | Before building Phase 2 |
| `phase3_environment_reconstruction.md` | Phase 3 methodology | ~10 min | Before building Phase 3 |
| `phase4_data_processing.md` | Phase 4 methodology | ~10 min | Before building Phase 4 |
| `phase5_analysis_execution.md` | Phase 5 methodology | ~10 min | Before building Phase 5 |
| `phase6_results_validation.md` | Phase 6 methodology | ~10 min | Before building Phase 6 |

---

## For a Coding Agent

If you are a coding agent generating the codebase from these documents:

1. Read `phase0_project_overview.md` first to establish context
2. Read all four operational docs (`ARCHITECTURE`, `STACK`, `SCHEMAS`, `GLOSSARY`) before writing any code
3. When implementing a specific phase, load that phase's methodology doc plus `SCHEMAS.md` and `ARCHITECTURE.md` into your active context
4. The Pydantic models in `SCHEMAS.md` are the canonical contract; if a phase doc and a schema disagree, follow the schema and flag the inconsistency
5. The naming conventions in `GLOSSARY.md` apply to every file you generate
6. The technology choices in `STACK.md` are locked; do not substitute alternatives without explicit instruction

---

## For a Human Collaborator

If you are joining the project:

1. Read `phase0_project_overview.md` to understand the goal
2. Skim `ARCHITECTURE.md` to understand the runtime model
3. Skim the six phase docs to understand the pipeline
4. Refer to `SCHEMAS.md`, `STACK.md`, and `GLOSSARY.md` as needed during implementation

The total reading time for the full documentation set is approximately 90 to 120 minutes. The system is designed to be implementable by a small team within a hackathon timeframe given this specification.

---

## Document Maintenance

These documents form a connected set. When changing one, check the others:

- Changes to `SCHEMAS.md` may require updates to phase docs that reference specific fields
- Changes to `STACK.md` may require updates to `ARCHITECTURE.md` if the tool's role changes
- Changes to phase docs may require updates to `SCHEMAS.md` if new artifacts or records are introduced
- New terms introduced anywhere should be added to `GLOSSARY.md`

The `GLOSSARY.md` is the slowest-moving document. Use it as the stability anchor — if you find yourself updating the glossary frequently, the project's vocabulary is still settling.

---

## Scope and Status

This documentation set defines the scope for v1 of the system, intended as the deliverable for the AMD Developer Hackathon (May 2026). Items deliberately left out of v1 scope are listed in `ARCHITECTURE.md` under "What Is Out of Scope for v1."
