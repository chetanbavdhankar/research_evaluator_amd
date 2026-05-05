# Knowledge Schema

This is the highest-authority schema for SpecCurve knowledge work. If a human or agent cannot express a claim using this schema, the claim is not ready to guide implementation.

## Required Metadata

Every durable fact, decision, assumption, feature, risk, and artifact must carry:

```yaml
confidence: high | medium | low
source: path-or-url-or-run-artifact
last_verified: YYYY-MM-DD
status: active | superseded | uncertain | rejected
owner_optional:
decision_id_optional:
```

Rules:

- `confidence: high` requires direct source support or completed verification.
- `confidence: medium` means plausible and sourced, but not implementation-verified.
- `confidence: low` means useful hypothesis only.
- `status: active` means build from it.
- `status: superseded` means keep for history, do not build from it.
- `status: uncertain` means do not treat as fixed.
- `status: rejected` means intentionally ruled out.

## Layer Hierarchy

SpecCurve knowledge lives in three operational tiers. The tier determines whether a claim may guide implementation.

| Tier | Folder | Lifecycle role | Build-from? |
|---|---|---|---|
| Control | `speccurve-wiki/0X-*.md` through `19-distribution-*.md`, plus `gate-status.md` | Active implementation contracts, decisions, and live readiness state. | YES |
| Review / Source | `speccurve-wiki/19-product-lens-review-v3.md`, `20-product-lens-brief.md` | Frozen-in-time critique and historical evidence backing the active contracts. | NO - read for context, do not build directly. |
| Archive | `speccurve-wiki/archive/*` | Superseded source preserved for traceability. | NO - re-promote into Control with a new decision record before building. |

Promotion rule: a fact in Review/Source or Archive can guide design only after it has been compiled into a Control page with `confidence`, `source`, and `last_verified` metadata, plus a corresponding entry in `13-decision-log.md` when it changes a contract.

## Consolidation Pipeline

Use this pipeline when new raw material enters the project:

| Layer | Location | Role | Promotion condition |
|---|---|---|---|
| Raw | `speccurve-kickoff/`, `brainstorm/`, external docs, interviews, run logs | Evidence intake and working notes. | Do not build directly. |
| Compiled | Control pages in `speccurve-wiki/` | Stable product, technical, demo, and risk contracts. | Requires confidence, source, last_verified, and status metadata. |
| Schema | `04-knowledge-schema.md` | The rules for expressing and promoting knowledge. | Update only when the knowledge model itself changes. |
| Artifact | `gate-status.md`, `user-validation-notes.md`, benchmark/report/spec/verifier outputs | Current evidence state and proof artifacts. | Update when a gate changes status or evidence appears. |

Raw or review-source claims can guide implementation only after they are compiled into a control page or evidence artifact with required metadata. This keeps the wiki from re-deriving decisions from older reviews.

## Entity Types

| Type | Required fields | Purpose |
|---|---|---|
| Product | `id`, `name`, `one_sentence`, `non_goals` | The thing being built. |
| User | `id`, `persona`, `workflow`, `pain`, `success_outcome` | The first user and use context. |
| Pain | `id`, `description`, `current_workaround`, `severity_notes` | Problem the product solves. |
| Feature | `id`, `purpose`, `inputs`, `outputs`, `acceptance_criteria` | Buildable product behavior. |
| Agent | `id`, `allowed_inputs`, `forbidden_behavior`, `output_schema`, `fallback` | Constrained LLM worker. |
| Dataset | `id`, `name`, `source_url`, `license`, `rows_optional`, `status` | Data allowed for analysis. |
| Paper | `id`, `title`, `authors`, `year`, `url_or_doi`, `dataset_id` | Published source for target claim. |
| Claim | `id`, `plain_english`, `outcome`, `predictor`, `expected_direction`, `limits` | Narrow statement tested by specs. |
| Specification | `id`, `claim_id`, `model_family`, `covariates`, `exclusion_rule`, `resampling`, `rationale` | Machine-readable analysis variant. |
| VerifierRule | `id`, `rule`, `reject_if`, `severity`, `message` | Deterministic or agent-assisted validation rule. |
| GPUWorkload | `id`, `operation`, `num_specs`, `num_resamples`, `device`, `batch_shape` | Numerical batch to run on MI300X. |
| Benchmark | `id`, `cpu_runtime`, `gpu_runtime`, `speedup`, `hardware_log`, `tolerance` | Evidence that AMD is load-bearing. |
| DemoMoment | `id`, `beat`, `screen`, `proof`, `time_budget_seconds` | Required demo sequence element. |
| Risk | `id`, `category`, `severity`, `likelihood`, `mitigation`, `kill_condition` | Failure mode and response. |
| Decision | `id`, `decision`, `rationale`, `supersedes_optional`, `status` | Durable product or architecture choice. |
| JudgingCriterion | `id`, `name`, `official_description`, `evidence_required` | Hackathon evaluation mapping. |
| SubmissionAsset | `id`, `asset_type`, `required_by`, `owner_optional`, `status` | Deliverable for final submission. |
| UserValidation | `id`, `respondent_type`, `artifact`, `questions`, `finding`, `status` | Evidence that the first user understands and values the report. |

## Relationship Types

| Relationship | Meaning | Example |
|---|---|---|
| `supports` | A strengthens B. | AMD proof panel `supports` Application of Technology. |
| `depends_on` | A cannot be valid without B. | Robustness surface `depends_on` result table. |
| `supersedes` | Newer decision replaces older claim. | SpecCurve framing `supersedes` replication framing. |
| `contradicts` | A conflicts with B and needs resolution. | Arbitrary uploads `contradicts` MVP scope. |
| `verifies` | A checks B. | VerifierRule `verifies` Specification. |
| `rejects` | A invalidates B. | Outcome-leakage rule `rejects` bad specification. |
| `uses` | A consumes B as input or tool. | GPUWorkload `uses` approved specifications. |
| `produces` | A emits B. | Statistics engine `produces` result table. |
| `demonstrates` | A is evidence for B. | CPU/GPU benchmark `demonstrates` MI300X load-bearing. |
| `risks` | A creates risk B. | Small dataset `risks` weak AMD proof. |
| `mitigates` | A reduces risk B. | Benchmark fairness contract `mitigates` unsupported AMD claim. |

## Entity Record Template

```yaml
id:
type:
name:
summary:
metadata:
  confidence:
  source:
  last_verified:
  status:
  owner_optional:
  decision_id_optional:
relationships:
  - type:
    target_id:
    evidence:
notes:
```

## Canonical Active Entities

| ID | Type | Name | Status | Confidence |
|---|---|---|---|---|
| P-SPECCURVE | Product | SpecCurve | active | high |
| U-REVIEWER | User | Statistically literate reviewer or methods instructor | active | medium |
| PAIN-MANUAL-ROBUSTNESS | Pain | Manual robustness checks are slow and fragmented | active | high |
| CLAIM-FINAL-TBD | Claim | Final target claim not selected | uncertain | high |
| DATASET-FINAL-TBD | Dataset | Final demo dataset not selected | uncertain | high |
| GPU-MI300X-BATCH | GPUWorkload | Batched regressions, bootstrap, permutation, specification sweeps | active | medium |
| GPU-BOOTSTRAP-FIRST | GPUWorkload | First prototype operation: batched bootstrap resampling | active | medium |
| UV-FIRST-USER | UserValidation | Lightweight reviewer/methods-user validation | active | medium |
| DEC-NON-REPLICATION | Decision | Do not frame as replication | active | high |

## Ingest Rules

When adding a new paper, dataset, run log, or build-session observation:

1. Extract entities first.
2. Attach required metadata.
3. Add relationships only when the edge is explicit or directly inferred from a cited source.
4. Mark uncertain facts as `uncertain`, not `active`.
5. If the new entity contradicts active knowledge, create or update a decision record before changing contracts.

## Contradiction Resolution

Prefer, in order:

1. Official hackathon source over local assumptions.
2. Newer decision records over older brainstorming docs.
3. Verified run artifacts over planned benchmark claims.
4. Deterministic verifier results over LLM explanations.
5. Narrow claims over broad product slogans.

If unresolved, mark both claims `uncertain` and add an open question in `13-decision-log.md`.
