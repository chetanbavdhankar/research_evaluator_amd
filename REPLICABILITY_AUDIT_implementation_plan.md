# REPLICABILITY-AUDIT

**Implementation Plan, v1.0 (handoff to coding agent)**

Owner: Chetan Bavdhankar
Date: May 2026
Scope: v0.1 astro-only, public eval set

---

## 0. How to use this document

This is a build specification, not an essay. It is written for a coding agent (or a competent collaborator) to translate directly into a working repository over roughly four weeks of focused effort. Every section is decision-locked. Where a choice has been made, the reason is given once and not revisited. Open questions are explicitly tagged `DEFERRED` with a target milestone for resolution. Anything not tagged `DEFERRED` is a binding constraint.

**Goal of v0.1:** a CLI named `replicability-audit` that ingests an astronomy paper (PDF or arXiv URL) and produces (a) a structured JSON audit, (b) a derived tier verdict using deterministic rules, (c) a markdown replication plan, and (d) an executable scaffold directory with real fetch scripts and analysis skeletons. The CLI must run end-to-end on the six papers in the v0.1 micro-benchmark before v0.1 ships.

**Anti-goals for v0.1:** multi-domain coverage beyond astro+generic, the substitution mode (regenerating plans against user-supplied open-access substitutes), web UI, hosted service, and any LLM-driven decision making in the scoring stage.

---

## 1. Product definition

### 1.1 What the CLI does

Single command, three subcommands:

```
replicability-audit ingest <paper>          # Stage 0+1: parse and extract
replicability-audit audit <paper>           # Stage 0..3: full audit JSON
replicability-audit plan <paper> [--exec]   # Stage 0..5: audit + plan + scaffold
```

`<paper>` accepts: a local PDF path, an arXiv ID (e.g., `2605.05650`), an arXiv URL, or a DOI. The `plan` subcommand with `--exec` generates the full executable scaffold directory under `./replication-<paper-id>/`. Without `--exec` it generates only the markdown plan and audit, no scaffold.

### 1.2 The eight-axis scorecard

The audit scores eight independent axes on a 0–3 scale. Each axis has a deterministic rubric encoded in code (see §4.4). The tier verdict is derived from these scores by a pure function (§1.3). The scorecard is the primary output; the tier is a summary.

| Axis | 0 — blocker | 1 — hard | 2 — workable | 3 — clean |
|---|---|---|---|---|
| **Data accessibility** | Gated, no substitute | Gated, near-substitute | Public, registration | Public, direct download |
| **Data identifiability** | Sources unnamed | Named, no version | Named + version | Named + version + DOI |
| **Method specification** | Hand-waved | Named, no params | Named + most params | Pseudocode + all params |
| **Software stack** | Unknown | Named, no versions | Named + versions | Lockfile / container |
| **Code availability** | None | Claimed, broken/private | Public, undocumented | Public, documented |
| **Compute footprint** | Infeasible (>1000 GPU-hr) | Heavy (>100 GPU-hr) | Moderate (laptop+GPU) | Trivial (laptop) |
| **Dependency closure** | Private upstream | Public, version-drifted | Public, stable | Self-contained |
| **Result verifiability** | No numerical claims | Plots only | Tabulated numbers | Tables + uncertainty |

### 1.3 Tier derivation rules (frozen)

1. **Tier 1** (full local replication): all axes ≥ 2, AND `data accessibility = 3`, AND `code availability ≥ 2`.
2. **Tier 2** (replication with caveats): no axis = 0, AND at most two axes scored at 1.
3. **Tier 3** (not locally replicable): any axis = 0, OR three or more axes at 1.

These rules are encoded as a pure Python function in `src/replicability_audit/scoring.py`. Changes to this function require updating the published benchmark scores. The function is unit-tested against hand-built audit fixtures.

---

## 2. Architecture

### 2.1 Pipeline stages

Six stages, strictly sequential, each writing a versioned artifact to a per-paper cache directory.

| # | Stage | Input | Output | Driver |
|---|---|---|---|---|
| 0 | **Ingest** | PDF / arXiv ID / DOI | `ParsedPaper` (sections, refs, tables, figures) | Deterministic |
| 1 | **Extraction** | `ParsedPaper` | `DataAsset[]`, `MethodStep[]`, `Software[]` | LLM (Sonnet) |
| 2 | **Resolution** | Extraction output + `DomainAdapter` | Each asset: download_recipe or documented blocker | Deterministic + archive APIs |
| 3 | **Scoring** | Resolved audit object | Eight axes, tier verdict, gap inventory | Deterministic |
| 4 | **Plan generation** | Audit + tier | `REPLICATION_PLAN.md`, `GAPS.md` | Templates + LLM (Opus, prose only) |
| 5 | **Scaffold codegen** | Audit + plan + recipes | `./replication-<id>/` directory | Deterministic codegen |

**Hard rule:** LLMs run only in stages 1 and 4. Stages 0, 2, 3, 5 are pure code with no model calls. This is the load-bearing decision of the architecture: it makes audits reproducible, scoring deterministic, and the system testable in CI without API keys.

### 2.2 The pluggable adapter protocol

Domain knowledge lives in adapters, not the core. v0.1 ships two adapters: `astro` and `generic`. Adding bio/chem/materials in later versions does not require core changes.

```python
# src/replicability_audit/adapters/base.py
from typing import Protocol
from ..models import ParsedPaper, DataAsset, ResolutionResult, Archive

class DomainAdapter(Protocol):
    name: str
    priority: int  # tie-break when multiple adapters claim a paper

    def detect(self, paper: ParsedPaper) -> float:
        """Return confidence in [0, 1] that this adapter handles the paper."""

    def known_archives(self) -> list[Archive]:
        """Archives this adapter can resolve against."""

    def resolve_dataset(
        self, asset: DataAsset, paper: ParsedPaper
    ) -> ResolutionResult:
        """Attempt to produce a download_recipe. Never raises; returns
        ResolutionResult with status in {resolved, partial, blocked, unknown}."""

    def standard_pipelines(self, instrument: str | None) -> list[str]:
        """Map 'standard reduction' phrases to concrete pipeline names
        (e.g., LRIS 2017 -> ['PypeIt', 'LPipe']). Empty list if unknown."""
```

### 2.3 Domain adapters in v0.1

| Adapter | Archives | Standard pipelines / tools |
|---|---|---|
| **astro** | KOA, MAST, ESO, IRSA, VizieR/CDS, ALMA, HEASARC, SDSS CAS, Gaia (via astroquery) | astroquery, PypeIt, LPipe, drizzlepac, astropy, specutils |
| **generic** | Zenodo, Figshare, OSF, Dataverse, GitHub, Hugging Face Datasets/Models | DOI resolution, repo health checks, dataset card parsing |

`generic` always runs as a fallback in addition to the primary adapter, because cross-cutting artifacts (a Zenodo-hosted code release for an astro paper) appear in every domain.

---

## 3. Data model

The data model is the contract between stages. All stages read and write Pydantic v2 models serialized as JSON. The audit JSON is the canonical artifact; everything else (markdown, scaffold) is derived from it.

### 3.1 Core models

```python
# src/replicability_audit/models.py
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class AccessSpec(BaseModel):
    kind: Literal["public_direct", "public_registration", "gated", "unknown"]
    notes: str = ""
    proprietary_until: datetime | None = None

class FetchScript(BaseModel):
    language: Literal["python", "bash"]
    body: str                        # the actual script text
    requires: list[str] = []         # python deps or system tools
    estimated_volume_mb: int | None = None

class DataAsset(BaseModel):
    id: str                          # stable, e.g. "lris-raw-2017a-w246"
    name: str
    kind: Literal["dataset", "catalog", "raw_obs", "reduced", "code", "model"]
    cited_in: list[str]              # section ids or "abstract"
    archive_hint: str | None         # "KOA", "MAST", or None
    identifiers: dict[str, str]      # {"program_id": ..., "doi": ..., "obs_date": ...}
    access: AccessSpec
    download_recipe: FetchScript | None = None
    resolution_log: list[str] = []   # stage 2 trace

class ParameterSpec(BaseModel):
    name: str
    value: str | float | int | bool | None = None
    underspecified: bool = False
    paper_quote: str | None = None   # the exact text from the paper

class MethodStep(BaseModel):
    order: int
    name: str
    inputs: list[str]                # DataAsset.id or prior step output ids
    outputs: list[str]
    parameters: list[ParameterSpec]
    software_used: list[str]         # Software.id values
    gap_flags: list[str]             # human-readable

class Software(BaseModel):
    id: str
    name: str
    version: str | None = None
    source: Literal["paper_explicit", "adapter_inferred", "standard_default"]

class Gap(BaseModel):
    severity: Literal["blocker", "high", "medium", "low"]
    axis: str                        # which scorecard axis it impacts
    description: str
    remediation_hint: str | None = None

class ComputeFootprint(BaseModel):
    cpu_hours: float | None = None
    gpu_hours: float | None = None
    storage_gb: float | None = None
    estimator_confidence: Literal["measured", "estimated", "guessed"]
    rationale: str

class AuditReport(BaseModel):
    paper_id: str                    # arXiv ID or DOI
    paper_title: str
    domain: str
    adapters_used: list[str]
    scorecard: dict[str, int]        # eight axes
    tier: Literal[1, 2, 3]
    data_inventory: list[DataAsset]
    method_pipeline: list[MethodStep]
    software_inventory: list[Software]
    gap_inventory: list[Gap]
    compute_estimate: ComputeFootprint
    decision_points: list[str]       # things the user must decide
    schema_version: str = "1.0"
    generated_at: datetime
    model_versions: dict[str, str]   # {"extractor": "claude-sonnet-4.6", ...}
    prompt_versions: dict[str, str]  # {"extract_data": "v3", ...}
```

### 3.2 JSON schema versioning

`AuditReport.schema_version` is bumped on any breaking change to the model. The CLI rejects audit JSONs with mismatched major versions. Migration scripts live in `src/replicability_audit/migrations/`.

---

## 4. Stage-by-stage specifications

### 4.1 Stage 0 — Ingest

- Resolve input to a canonical paper id: arXiv → `arxiv:2605.05650`, DOI → `doi:10.1093/mnras/...`.
- If input is a URL or ID, download the PDF via the `arxiv` package or unpaywall.org.
- Parse PDF with `pymupdf` (text + layout) and `pdfplumber` (tables). Extract sections by heading detection; if heading detection fails, fall back to whole-document text with `section=null`.
- Resolve references using the bibliography section + Crossref API. Store as `Reference` objects with bibcode/arXiv-id/DOI where available.
- Detect domain via journal name + keywords + arXiv category. Multi-label allowed. v0.1 only routes `astro` and `generic`.
- Cache artifact: `cache/<paper-id>/parsed.json`

### 4.2 Stage 1 — Extraction

Four LLM calls in parallel, each with a strict JSON schema enforced via the Anthropic API tool-use mechanism. Model: claude-sonnet (latest available). Temperature 0. Max output tokens 8000 per call.

- `extract_data`: returns `DataAsset[]` with kind, archive_hint, identifiers, paper section quotes.
- `extract_methods`: returns `MethodStep[]` with parameters list (each parameter flagged `underspecified=true` if no value given).
- `extract_software`: returns `Software[]` with version where stated.
- `extract_compute`: returns `ComputeFootprint` with `estimator_confidence='guessed'` unless paper explicitly quotes hours/cores.

Each prompt lives in `prompts/extraction/<name>.md` and is committed. Prompt version is part of the audit JSON.

Cache artifact: `cache/<paper-id>/extracted.json`

### 4.3 Stage 2 — Resolution

For each `DataAsset`, the active adapters attempt to produce a `FetchScript`. The deterministic resolution loop is:

1. Detect which adapter(s) apply to the asset (astro adapter handles `archive_hint` in {KOA, MAST, ESO, ...}; generic handles DOIs and GitHub URLs).
2. Adapter calls archive APIs to verify the asset exists and to retrieve canonical query parameters.
3. Adapter constructs the `FetchScript` from a versioned template (`templates/fetch/<archive>.j2.py`).
4. Every URL emitted by the LLM in Stage 1 is HEAD-tested before inclusion in the recipe. URLs that 404 are logged in `resolution_log` and the asset is downgraded one accessibility level.
5. If an asset cites a prior paper as its data source (e.g., "sample from Green 2014"), the resolver fetches that paper, extracts its data section recursively (depth limit: 1), and merges the resolved upstream into the current paper's audit.

**Network failure policy:** each archive call retries 3× with exponential backoff (1s, 4s, 16s). On total failure, the asset's access is set to `unknown` with `notes='archive unreachable on YYYY-MM-DD'`. The audit is marked `tentative=true`. Tentative audits do not affect the published benchmark.

Cache artifact: `cache/<paper-id>/resolved.json`

### 4.4 Stage 3 — Scoring

Pure function. No LLM, no network, no I/O. Implementation skeleton:

```python
# src/replicability_audit/scoring.py
def score_data_accessibility(audit) -> int:
    statuses = [a.access.kind for a in audit.data_inventory]
    if any(s == "gated" for s in statuses) and not any_substitute_available(audit):
        return 0
    if any(s == "gated" for s in statuses):
        return 1
    if any(s == "public_registration" for s in statuses):
        return 2
    return 3

# ... seven more axis scorers, each ~10 lines

def derive_tier(scorecard: dict[str, int]) -> int:
    vals = list(scorecard.values())
    if (all(v >= 2 for v in vals)
        and scorecard["data_accessibility"] == 3
        and scorecard["code_availability"] >= 2):
        return 1
    if all(v != 0 for v in vals) and sum(1 for v in vals if v == 1) <= 2:
        return 2
    return 3
```

Each scorer is independently unit-tested with at least three fixture audits per axis (hand-built, covering each score level). Scorer changes require a CHANGELOG entry and a benchmark re-run.

### 4.5 Stage 4 — Plan generation

Templated 80%, LLM 20%. The plan is assembled from Jinja2 templates in `templates/plan/<tier>.md.j2` with LLM-generated prose interpolated into specific named slots: `{{ gap_synthesis }}`, `{{ substitution_suggestions }}`, `{{ executive_summary }}`.

- Tier 1 → `templates/plan/tier1.md.j2`: full step-by-step with acceptance criteria, no caveat section.
- Tier 2 → `templates/plan/tier2.md.j2`: same structure plus a "decision points" section with LLM-synthesized prose for each gap.
- Tier 3 → `templates/plan/tier3.md.j2`: short doc, mostly the gap inventory + a "do not proceed without remediation" note. No execution scaffold is generated for Tier 3.

LLM call here uses Opus, temperature 0.3 (slightly higher than extraction because prose quality matters more than determinism). Outputs are reproducible enough because the templated structure dominates.

### 4.6 Stage 5 — Scaffold codegen

Pure code generation, no LLM. Produces a directory tree:

```
replication-<paper-id>/
├── README.md                # generated from template, includes tier badge
├── AUDIT.json               # the full audit object
├── REPLICATION_PLAN.md      # from Stage 4
├── GAPS.md                  # gap inventory, sorted by severity
├── DECISIONS.md             # blank template for the user to fill in
├── pyproject.toml           # deps from software_inventory, pinned via uv
├── .python-version          # 3.12
├── data/                    # gitignored, fetch scripts populate this
│   └── .gitkeep
├── scripts/
│   ├── 00_fetch_<archive>.py   # one per resolved DataAsset
│   ├── 01_preprocess.py        # skeleton with TODO(gap-N) markers
│   ├── 02_analyze.py           # skeleton
│   ├── 03_compute_results.py   # skeleton
│   └── 04_validate.py          # compares against paper's tables
├── tests/
│   ├── test_fetch_scripts_smoke.py
│   └── test_analysis_skeletons_import.py
└── notebooks/
    └── exploration.ipynb    # empty, set up with imports
```

Each `00_fetch_*.py` is a real, runnable script generated by inlining the `FetchScript.body` from the corresponding `DataAsset`. The scripts include a `--dry-run` flag that prints the planned download size and exits without fetching.

**`04_validate.py` is the most important generated file.** For papers where the audit extracted numerical claims (Table 1, headline results), this script reads the paper's tables (cached in Stage 0), reads the user's reproduced results, and emits a per-row diff report with configurable tolerance. It exits non-zero if reproduction is outside tolerance. This is what makes the system honest about whether replication actually worked.

---

## 5. Repository layout

```
replicability-audit/
├── pyproject.toml           # uv-managed, Python 3.12
├── README.md
├── BENCHMARK.md             # eval set results, regenerated on every release
├── CHANGELOG.md
├── DECISIONS.md             # the record of every binding choice
├── prompts/                 # version-controlled, not in code
│   ├── extraction/
│   │   ├── extract_data.md
│   │   ├── extract_methods.md
│   │   ├── extract_software.md
│   │   └── extract_compute.md
│   └── plan/
│       └── prose_synthesis.md
├── templates/               # Jinja2, version-controlled
│   ├── plan/
│   │   ├── tier1.md.j2
│   │   ├── tier2.md.j2
│   │   └── tier3.md.j2
│   ├── fetch/
│   │   ├── koa.j2.py
│   │   ├── mast.j2.py
│   │   ├── vizier.j2.py
│   │   ├── sdss_cas.j2.py
│   │   ├── zenodo.j2.py
│   │   └── github.j2.py
│   └── scaffold/
│       ├── README.md.j2
│       ├── pyproject.toml.j2
│       └── 04_validate.py.j2
├── src/replicability_audit/
│   ├── __init__.py
│   ├── cli.py               # typer app
│   ├── config.py            # settings, paths, model pinning
│   ├── models.py            # all Pydantic models
│   ├── ingest.py            # Stage 0
│   ├── extraction.py        # Stage 1
│   ├── resolution.py        # Stage 2 orchestrator
│   ├── scoring.py           # Stage 3 (pure)
│   ├── planning.py          # Stage 4
│   ├── scaffold.py          # Stage 5
│   ├── llm.py               # thin Anthropic wrapper, retries, logging
│   ├── cache.py             # per-paper cache management
│   ├── adapters/
│   │   ├── base.py          # the Protocol
│   │   ├── astro.py
│   │   └── generic.py
│   └── archives/            # archive-specific clients
│       ├── koa.py
│       ├── mast.py
│       ├── vizier.py
│       ├── sdss.py
│       └── zenodo.py
├── benchmark/
│   ├── papers/              # PDFs of the eval set, gitignored if licensing forbids
│   ├── ground_truth/
│   │   ├── 2605.05650.json  # one file per paper, with full justification
│   │   └── ...
│   ├── run_benchmark.py
│   └── results/             # one subdir per release tag
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

---

## 6. Build order — eight milestones

The most important sequencing change from earlier drafts: the eval set is built at M2.5, not M7. M3 onward is driven by it.

### M1 — Skeleton + ingest (3–5 days)

- Repo, pyproject, uv lock, Python 3.12, GitHub repo with CI scaffold.
- Typer CLI with stub subcommands. Logging via structlog.
- PDF parsing with pymupdf + pdfplumber, section detection.
- arXiv/DOI/URL resolution via the `arxiv` package and Crossref API.
- Domain detector: keyword + arXiv category lookup. Returns labels with confidences.
- **Acceptance:** `replicability-audit ingest <paper>` runs on at least three test papers and emits a valid `parsed.json` with sections, references, tables.

### M2 — Extraction (5–7 days)

- LLM wrapper with retry, timeout, model pinning, and prompt-version tagging.
- Four extraction prompts in `prompts/extraction/`. Each has an input/output JSON schema in the same file.
- Anthropic tool-use enforcement of structured output. No free-text JSON parsing.
- Extraction tests: hand-curated "expected output" for each test paper, diff scoring on key fields.
- **Acceptance:** `replicability-audit audit <paper>` populates `data_inventory`, `method_pipeline`, `software_inventory` on the same three test papers, with extraction tests passing.

### M2.5 — Eval set v0 (3–4 days)

*Critical milestone. Stops if it slips.*

- Pick six astro papers: 2 Tier 1, 2 Tier 2, 2 Tier 3. The Fernández-Figueroa 2026 paper is one of the Tier 3s.
- For each, write a `ground_truth/<id>.json` with: full scorecard with per-axis justification (1–2 sentences each, with a paper quote where relevant), final tier verdict, and a list of "ground-truth gaps" the system should detect.
- Each paper requires 1–2 hours of careful manual review. Budget: 12 hours.
- Commit a `benchmark/run_benchmark.py` that runs the audit on each paper and produces a confusion matrix + gap-recall scores.
- **Acceptance:** Benchmark runs end-to-end. Initial scores will be poor (M3+ improves them). Existence and runnability of the benchmark is the milestone, not the score.

### M3 — Astro adapter + resolution (7–10 days)

- Adapter implementing `detect`, `known_archives`, `resolve_dataset`, `standard_pipelines`.
- Archive clients: KOA TAP query builder, MAST via astroquery, VizieR via astroquery, SDSS CAS query templates.
- Reference-chase recursion (depth limit 1).
- Resolution loop with retry/backoff per §4.3.
- "Standard pipeline" lookup table: instrument + era → recommended pipeline. v0.1 covers LRIS, KCWI, MOSFIRE, ACS, WFC3, MUSE, X-Shooter.
- **Acceptance:** Benchmark gap-recall ≥ 0.6 on the four astro papers. Every astro `DataAsset` on Tier 1/2 papers has a runnable `download_recipe`.

### M4 — Generic adapter (3–5 days)

- Zenodo DOI lookup, GitHub repo health check (HEAD on README + pyproject), Hugging Face dataset/model resolution.
- OSF and Dataverse via their public APIs.
- Always runs alongside primary adapter, results merged.
- **Acceptance:** Cross-cutting artifacts (Zenodo code drops on astro papers) are correctly resolved. Benchmark gap-recall improves by ≥ 0.1 over M3 baseline.

### M5 — Scoring + tier derivation (2–3 days)

- Eight axis scorers as pure functions, each with ≥3 unit-test fixtures.
- `derive_tier` function with comprehensive table-driven tests.
- Wire into CLI: `replicability-audit audit` now produces a valid `AuditReport` with scorecard + tier.
- **Acceptance:** Tier verdict accuracy ≥ 5/6 on the eval set. Per-axis scores within ±1 of ground truth on average.

### M6 — Plan generation + scaffold codegen (5–7 days)

- Three Jinja2 plan templates (tier1/2/3).
- LLM prose synthesis for the named slots only. Opus, temperature 0.3.
- Scaffold codegen: directory tree, fetch scripts inlined from `FetchScript.body`, skeleton analysis scripts with `TODO(gap-N)` markers, validate.py template.
- Smoke tests: every generated fetch script must `python -c 'import <script>'` cleanly. Every generated `--dry-run` must exit 0.
- **Acceptance:** `replicability-audit plan <paper> --exec` runs on all six benchmark papers. For Tier 1/2 papers, generated `00_fetch_*.py` scripts execute end-to-end and download real files in a clean environment.

### M7 — Validation harness + benchmark publication (5–7 days)

- Expand eval set from 6 to 25 papers (+8 Tier 1, +6 Tier 2, +3 Tier 3, +2 adversarial).
- Each new paper needs the same 1–2 hour manual review. Budget: 38 hours.
- Automated benchmark scoring: tier accuracy, per-axis MAE, gap recall@k, fetch-script success rate, validate.py numerical recovery on Tier 1 papers.
- `BENCHMARK.md` is regenerated by `run_benchmark.py` and committed on every release.
- Public release: GitHub repo, Zenodo DOI for the benchmark, blog post.
- **Acceptance:** Tier verdict accuracy ≥ 0.8 across 25 papers. Gap recall ≥ 0.7. Public benchmark online with a stable DOI.

### M8 — Iteration and adapter expansion (ongoing, post-v0.1)

- v0.2: bio adapter (NCBI, EBI, AlphaFold DB) + 5 bio papers in eval set.
- v0.3: chem adapter + materials adapter + 5 papers each.
- v0.4: substitution mode.

### Calendar reality

Sum of focused-work estimates M1–M7: roughly 30–40 days of full-time work. With a day job, partner travel, AMD hackathon (May 2026), and the Marathi rap project active, calendar time to v0.1 is realistically 10–14 weeks. Plan against that, not the focused-work sum.

---

## 7. Decisions ledger (frozen)

Every decision below is binding. Changing one requires a CHANGELOG entry, a benchmark re-run, and a major-version bump if the change is breaking.

| Decision | Choice | Rationale |
|---|---|---|
| Domain scope v0.1 | astro + generic only | Quality over breadth; you have astro taste. |
| Eval-set timing | Built at M2.5, drives M3+ | Avoid optimizing against intuitions. |
| Eval-set publication | Public, Zenodo DOI | Citable artifact; forces rigor. |
| Substitution mode | Deferred to v0.4 | Pulls toward subjective scoring; out of scope. |
| LLM in scoring stage | Forbidden | Determinism is load-bearing. |
| LLM in plan stage | Prose only, ≤20% of output | Templates dominate; LLM fills slots. |
| Model pinning | Pinned in config; recorded per audit | Reproducibility across model upgrades. |
| Prompt versioning | Files in `prompts/`, recorded per audit | Prompts are code. |
| Prompt-regression CI | Eval set runs on every prompt change | Catches silent quality regressions. |
| Compute footprint estimator | Lookup table per method family + paper-quoted hours; `estimator_confidence` emitted | Most accurate option without dynamic profiling. |
| Archive retry policy | 3 retries, exp backoff; soft-fail with `tentative=true` | Same paper, different day, same verdict. |
| Validate step grading | Numerical, with tolerance; non-zero exit on miss | "Code runs" is not enough. |
| Audit JSON schema versioning | `schema_version` field; major-version gate | Old audits stay readable. |
| Tier rules | Frozen as in §1.3 | Auditable, defensible, code-encoded. |

### Deferred items (resolve before milestone listed)

- **DEFERRED (M2):** Exact LLM model identifier and rate-limit policy. Decide when integrating the SDK.
- **DEFERRED (M3):** KOA TAP query authentication. KOA permits anonymous queries on public data; verify with a smoke call on day 1 of M3.
- **DEFERRED (M6):** Numerical tolerance for `validate.py`. Likely 5% relative error for headline numbers, 20% for individual data points; finalize during M6 from observed scatter on Tier 1 papers.
- **DEFERRED (M7):** Whether benchmark PDFs are committed to the repo (licensing). Default: arXiv DOIs and ground-truth JSONs only; PDFs fetched at benchmark-run time.

---

## 8. Stack

### 8.1 Pinned versions

| Component | Choice | Why |
|---|---|---|
| Language | Python 3.12 | Astro stack support; new typing. |
| Package manager | uv | Fast, reproducible locks. |
| CLI framework | typer | Type-driven; minimal boilerplate. |
| Models | pydantic v2 | JSON schema, validation, fast. |
| LLM SDK | anthropic | Tool-use for structured output. |
| Models used | Sonnet (extraction), Opus (plan prose) | Cost vs. quality trade-off; pinned. |
| PDF parsing | pymupdf + pdfplumber | Text + tables. |
| HTTP | httpx (async) | Parallel archive resolution. |
| Archive APIs | astroquery, pyvo | Standard astro tooling. |
| Templates | jinja2 | Plan + codegen. |
| Logging | structlog | JSON logs to a file per audit. |
| Tests | pytest + pytest-recording | Mock archive APIs reproducibly. |
| Cache store | SQLite + JSON files | No DB server; per-paper directories. |
| CI | GitHub Actions | Tests on PR; benchmark on tag. |

### 8.2 What is NOT in the stack (deliberately)

- No web framework. CLI only.
- No database server. SQLite + files.
- No orchestrator (Airflow, Prefect). Stages run in-process.
- No LangChain/LangGraph. Direct Anthropic SDK calls; the workflow is short and structured enough that a framework adds noise.
- No vector DB. No embedding-based retrieval. Reference resolution is structured (Crossref API, arXiv lookups), not semantic search.

---

## 9. Quality, testing, CI

### 9.1 Test layers

- **Unit:** scoring functions, tier derivation, model serialization, prompt schema validation. Fast, no network, no API.
- **Integration:** each archive client against recorded HTTP fixtures (pytest-recording / VCR). Re-record monthly.
- **End-to-end:** the six benchmark papers, full pipeline. Runs on tags, not on every PR (uses real API keys).
- **Smoke:** generated fetch scripts must import and `--dry-run` cleanly.

### 9.2 CI matrix

- On PR: unit + integration tests, type-check (mypy strict), lint (ruff), prompt-schema validation.
- On prompt change (any file in `prompts/`): also runs the M2.5 micro-benchmark and fails if scores regress > 5%.
- On tag (release): full M7 benchmark, `BENCHMARK.md` regenerated, PR auto-opened with the diff.

### 9.3 Definition of Done for v0.1

1. All eight milestones complete (M1–M7).
2. Tier verdict accuracy ≥ 0.8 on 25-paper benchmark.
3. Gap recall ≥ 0.7.
4. All Tier 1 benchmark papers reproduce headline numbers within tolerance via `04_validate.py`.
5. `BENCHMARK.md` and a Zenodo DOI are public.
6. `README.md` includes a working quickstart that runs end-to-end on at least one Tier 1 paper without manual intervention beyond credentials.
7. `CHANGELOG.md` and `DECISIONS.md` are current.

---

## 10. Risks and mitigations

| Risk | Likelihood × Impact | Mitigation |
|---|---|---|
| LLM extraction returns wrong-shaped JSON | Medium × High | Tool-use enforcement; pydantic validation; hard-fail with diff vs. schema. |
| Archive API breaks or changes shape | Medium × Medium | VCR fixtures, monthly re-record, version-pinned astroquery. |
| Prompt drift across model upgrades | High × Medium | Pinned model + prompt-version-CI + benchmark gate. |
| Tool-polish eats meta-science time | High × High | M7 acceptance is publication, not perfection. Move to meta-science survey at v0.1. |
| Benchmark ground-truth disagreement | Medium × High | Per-axis written justification; one external reviewer on the v0.1 set. |
| Scope creep into other domains | High × Medium | v0.1 ships astro-only. Period. New domains are versioned releases. |
| Calendar slip from focused-work miscount | High × Medium | Weekly slip review; M2.5 is the kill-switch checkpoint. If M2.5 isn't done by week 4, descope to 4 papers. |

---

## 11. Beyond v0.1

Versioned roadmap. Each version is releasable on its own.

- **v0.2:** bio adapter (NCBI, EBI, GEO, AlphaFold DB) + 5 bio papers in eval set.
- **v0.3:** chem and materials adapters; eval set grows to ≥40 papers.
- **v0.4:** substitution mode — user supplies open-access substitutes; pipeline regenerates plan around them.
- **v0.5:** meta-science release — run pipeline across 200+ recent astro letters; publish distribution of tier verdicts as a paper. The tool was always the means; this is the end.

---

## 12. Handoff checklist for the coding agent

1. Read this document end-to-end. Flag any ambiguity before writing code.
2. Initialize the repo with the layout from §5. Commit the empty tree first.
3. Begin M1. Do not skip ahead. Each milestone has explicit acceptance criteria; pass them before moving on.
4. M2.5 is the most fragile milestone. If the eval set isn't built before M3 starts, stop and build it. Do not negotiate.
5. Every prompt change runs the M2.5 benchmark in CI. Do not bypass.
6. Every binding decision in §7 is law. If a real reason emerges to revisit one, update `DECISIONS.md`, `CHANGELOG.md`, and re-run the benchmark.
7. Ship v0.1 when DoD (§9.3) is met. Not before.

---

*— end of document —*
