# Product Lens Brief — SpecCurve + Wiki Audit

> REVIEW/SOURCE PAGE - DO NOT BUILD DIRECTLY FROM THIS FILE.
> Current implementation authority lives in the control pages and `gate-status.md`.
> Checklist items below are historical recommendations; compiled fixes should be checked in the relevant control page.

Skill used: `/everything-claude-code:product-lens` (modes: Founder Review + Mode-1 Diagnostic + Wiki audit)

Review target:

```text
amd-hackathon-plan/brainstorm/      (raw idea pool + codex meta-review)
amd-hackathon-plan/speccurve-kickoff/ (raw kickoff source set)
amd-hackathon-plan/speccurve-wiki/   (compiled wiki — this is the audit target)
```

Reference compared against:

```text
https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2  (LLM Wiki v2, extends Karpathy)
```

Review date: `2026-05-05`

Metadata:

```yaml
confidence: high
source: speccurve-wiki/* (read in full); brainstorm/RANKED-IDEAS.md; brainstorm/codex-review/SYNTHESIS-DELTA.md; rohitg00 gist
last_verified: 2026-05-05
status: active
supersedes_optional: complements 19-product-lens-review-v3.md (does not replace it)
```

---

## Verdict

```text
GO for deterministic-spine implementation immediately.
NOT YET GO for app shell, agents, or build-in-public posts.
Single P0 blocker is unchanged from V3: dataset/claim is not selected.
```

The wiki passes the founder review at 8.4/10. The product brief passes the seven-question diagnostic at 8.4/10. The wiki passes the rohitg00-gist v2 audit at 7.0/10 — adoption is high on structure (schema, supersession, confidence, graph, crystallization) and intentionally low on scale/automation features (hybrid search, event hooks, decay, mesh sync) that a 7-day, ~30-page hackathon wiki does not need.

---

## Part 1 — Founder Review (Mode 2)

Inferred product, scored independently from the wiki's self-assessment.

### What is this trying to be?

```text
A reviewer-grade specification-robustness-analysis tool that turns one public
research claim into an MI300X-executed robustness surface and exportable report,
designed to win the AMD Developer Hackathon by making the GPU structurally
load-bearing instead of decorative.
```

### PMF signals scorecard (0-10)

| Signal | Score | Evidence |
|---|---:|---|
| Usage growth trajectory | n/a | Pre-build; no users yet. |
| Retention indicators | n/a | Pre-build. |
| Revenue signals | 0 | No pricing/billing intent — correct for hackathon. |
| Competitive moat | 7 | Verifier + provenance + GPU+surface combo is hard to copy in 7 days; the moat against post-hackathon competitors is dataset trust and benchmark honesty, not code. |
| Demo-day judgability | 9 | All four LabLab criteria mapped 1:1 with required artifacts in `02-hackathon-judging-map.md`. |
| Anti-wrapper defense | 8 | Statistics in deterministic code, agents constrained to JSON; collapsing the agents into one prompt does NOT preserve the product (verifier rejection is the load-bearing live beat). |
| Distribution alignment | 8 | Hugging Face Space + two technical updates aligned to LabLab extra-challenge surface. |

### The one thing that would 10x this

```text
Lock the final paper/dataset/claim today, reproduce the baseline tomorrow,
and run the first fair CPU-vs-MI300X batched-bootstrap benchmark by end of
this week. Everything else in the wiki is ready to consume that artifact.
```

### Things being built that don't matter (cut or defer)

| Item | Why cut/defer | Decision |
|---|---|---|
| Proposer LLM agent before deterministic spec grid hits 50 valid specs | Wiki already flags ICE = 3.0; deterministic fallback exists; risk of feeling decorative. | Defer to P2. Build deterministic generator first. |
| Polished PDF report | MVP wiki contract says Markdown/JSON; PDF is a polish task. | Defer post-submission. |
| Build-in-public Update 1 before D-006 (dataset) is closed | "Why one p-value is not enough" is safe, but posting before product-wording is locked risks rework. | Hold until baseline gate passes. |
| Arbitrary upload, multi-paper, fine-tuning, statistical IDE | Already enumerated as anti-goals. | Continue rejecting. |
| Permutation kernel before bootstrap kernel works | D-007 sequenced this correctly; permutation is operation #2. | Continue per build sequence. |

---

## Part 2 — Diagnostic (Mode 1, seven questions)

V3 already ran this. Below is the delta + my independent re-grade.

| Q | V3 score | My score | Delta reason |
|---|---:|---:|---|
| 1. Who is this for? | 8.5 | 8.5 | Persona is concrete; validation plan exists but unrun. |
| 2. What is the pain? | 7.5 | 7 | Before/after table is good but pain is still asserted, not measured (no "X reviewers told us they spend Y hours"). |
| 3. Why now? | 8 | 8 | Conditional on benchmark — fair. |
| 4. 10-star version? | 8 | 8 | Aspirational without contaminating MVP — clean. |
| 5. MVP? | 9 | 9 | Tight: one paper, one dataset, one claim, 200+ specs, ≥3 rejected, fair benchmark, surface, report. |
| 6. Anti-goal? | 9 | 9 | Seven explicit no's including no-replication-framing and no-truth-verdict — unusually strong. |
| 7. How do we know it's working? | 8.5 | 8 | Eval gates are excellent; product metrics depend on artifacts that don't exist yet. |
| **Overall** | **8.35** | **8.4** | Effectively unchanged. |

I disagree with V3 on one minor point: pain (Q2) should be 7, not 7.5 — the user-validation plan is great but the "spend hours or days" claim has no real-reviewer reference. Closing this is a 60-minute task: ask one methods PhD how long their last robustness check took.

---

## Part 3 — Wiki Audit Against rohitg00 LLM Wiki v2

The gist's central additions to Karpathy's original were: **lifecycle**, **knowledge graph**, **scale**, **automation**, **quality**, **collaboration**, **privacy**, **crystallization**, **multi-format output**, and **schema-as-product**. Here's the SpecCurve wiki's adoption depth.

### Adoption scorecard

| Gist v2 capability | Adopted? | Evidence in SpecCurve wiki | Score |
|---|---|---|---:|
| Three-layer architecture (raw / wiki / schema) | YES | `speccurve-kickoff/` is raw; `speccurve-wiki/*.md` is wiki; `04-knowledge-schema.md` is schema declared "highest-authority". | 10 |
| Schema as the real product | YES | `04-knowledge-schema.md` literally states it is the highest authority; agents must express claims in this schema. | 10 |
| Confidence scoring | YES | `confidence: high/medium/low` required on every durable claim per `00-operating-manual.md`. | 9 |
| Supersession (linked, timestamped) | YES | `supersedes` / `superseded_by` relationship; `13-decision-log.md` carries SD-001..SD-004 with reasons + replacement IDs. | 9 |
| Forgetting / retention decay | NO | All decisions kept forever; no Ebbinghaus curve, no auto-deprioritization. | 3 |
| Consolidation tiers (working → episodic → semantic → procedural) | PARTIAL (implicit) | Brainstorm = working, codex SYNTHESIS-DELTA = episodic, wiki = semantic, schema/contracts = procedural. Not formally labeled but topologically present. | 6 |
| Entity types | YES | 17 typed entities (Product/User/Pain/Feature/Agent/Dataset/Paper/Claim/Specification/VerifierRule/GPUWorkload/Benchmark/DemoMoment/Risk/Decision/JudgingCriterion/SubmissionAsset/UserValidation). | 10 |
| Typed relationships | YES | 11 relationship types (supports, depends_on, supersedes, contradicts, verifies, rejects, uses, produces, demonstrates, risks, mitigates). | 10 |
| Graph traversal for queries | PARTIAL | `05-entity-graph.md` provides mermaid + edge table; no programmatic traversal. Fine for 30-page wiki, would not scale to 300. | 6 |
| Hybrid search (BM25 + vector + graph) | NO | Single `index.md` + manual `03-source-map.md`. | 2 |
| Event-driven automation hooks (auto-ingest, auto-lint, auto-context) | NO | All updates manual ("update the wiki in the same session" per operating manual). | 2 |
| Quality scoring | PARTIAL | `14-quality-lint.md` enumerates checks but does not produce a numeric score per page. | 5 |
| Self-healing (auto-fix orphans, broken links) | PARTIAL | Lint identifies; humans fix. The "SUPERSEDED SOURCE PAGE" banners are a good in-place healing pattern. | 5 |
| Contradiction resolution with precedence | YES | `04-knowledge-schema.md` line 113-122 lists explicit precedence order (official source → newer decision → run artifact → deterministic verifier → narrow claim). | 9 |
| Multi-agent / mesh sync | N/A | Single 3-person team, single namespace; not needed for hackathon. | n/a |
| Privacy / governance / denylist | PARTIAL | Strong anti-overclaiming and "no fake AMD numbers" rules; no explicit secret-redaction rule for ingest. Risk is low because all sources are public. | 6 |
| Crystallization (filing back exploration results) | YES | The wiki itself IS a crystallization of brainstorm → codex meta-review → SYNTHESIS-DELTA. Decisions log preserves the chain. | 9 |
| Multi-format output (beyond markdown) | YES | Markdown wiki + JSON contracts (benchmark, spec, verifier rule outputs); deterministic code emits artifacts; report exports MD or JSON. | 8 |

**Aggregate: 7.0/10.**

### What this score means

The wiki adopted the **structural** half of the gist (schema, supersession, confidence, graph, crystallization, contradiction precedence) at 9-10/10. It intentionally skipped the **scale and automation** half (hybrid search, event hooks, decay, auto-healing, quality scoring) at 2-5/10. For a 7-day, ~30-page wiki with one team and one product, that is the **correct triage** — those features add value at hundreds of pages and across multiple sessions, both of which are post-hackathon concerns.

The gist itself supports this triage in its "Implementation Spectrum" section: *"Minimal viable wiki: raw sources + wiki pages + index.md + a schema that describes ingest/query/lint workflows. This is roughly what the original describes. It works. Start here."* SpecCurve has gone past minimal (it adopted lifecycle + structure + crystallization), and stopped short of scale + automation. That is precisely the recommended landing zone.

### Where the gist exposes a real gap

Only one finding from the audit is a hackathon-relevant fix:

**Gap A — No formal consolidation pipeline.** The brainstorm/kickoff/wiki layers exist, but the relationship is documented in prose, not in the schema. If the team adds another raw source (e.g., a paper PDF, a chat with an AMD dev-rel person), there is no rule for *which layer it lands in* and *when it gets promoted*. Karpathy's "compile, don't re-derive" insight depends on this pipeline being explicit.

**Fix:** Add a 3-line block to `04-knowledge-schema.md`:

```text
Layer 1 (raw):     speccurve-kickoff/, brainstorm/, decisions/<id>-evidence/
Layer 2 (compiled): speccurve-wiki/0X-*.md
Layer 3 (schema):  speccurve-wiki/04-knowledge-schema.md
Promotion rule: a fact in raw can guide design only after it appears in
                a compiled page with confidence + source + last_verified.
```

This is a 5-minute edit, does not require new infrastructure, and closes the only gist-relevant gap that matters at hackathon scale.

### What does NOT need fixing (despite low scores)

| Capability | Score | Why we skip |
|---|---:|---|
| Hybrid search | 2 | 30 pages fit in `index.md`; LLM can read the whole index in one pass. |
| Auto-ingest hooks | 2 | One team, one shared session model; manual updates have lower failure rate than half-built automation in 7 days. |
| Retention decay | 3 | Hackathon timeline is shorter than any reasonable decay half-life. |
| Quality auto-scoring | 5 | Manual lint runs before each gate; that is sufficient cadence for the build window. |
| Mesh sync | n/a | Single team. |

---

## Part 4 — Founder-Lens Risks Not Already in `12-risk-register.md`

The risk register is strong. Three additional product-lens risks I would add:

| ID | Risk | Severity | Likelihood | Mitigation | Kill condition |
|---|---|---|---|---|---|
| R13 | Distribution work begins before product-wording is locked, requiring a post-publication retraction. | medium | medium | Hold both LinkedIn/X updates until baseline gate passes; draft both as PRs in repo first. | Update goes live before D-006 closes. |
| R14 | The team treats the codex meta-review's "BinderForge backup" pattern as still active and pivots back if SpecCurve's first benchmark stalls. | medium | low-medium | Decision log already supersedes this; add a single line to `13-decision-log.md` stating BinderForge pivot is rejected, not paused. | Build energy is spent restoring BinderForge after Day 3. |
| R15 | Pain quantification gap (Q2 = 7, not 7.5) leaves business-value pitch soft for judges. | low | medium | One 30-min call with a methods PhD before submission to get a real "I spend X hours per review" anchor. Quote in slide deck. | Submission narrative uses only hypothetical pain language. |

---

## Part 5 — Concrete Next-Step Checklist

The wiki has a build sequence (`16-build-sequence.md`); this checklist is the **product-lens overlay** — the things the build sequence assumes will happen but that someone has to actually trigger.

Today (next 24 hours):

- [ ] Score 3-5 candidate datasets using the rubric in `08-data-and-claim-contract.md` § Dataset Scoring Rubric. Time-box to 90 minutes.
- [ ] Fill `decisions/0001-final-dataset-and-claim.md`. This closes D-006 and unblocks every downstream gate.
- [ ] Add the 5-line consolidation-layer block to `04-knowledge-schema.md` (Gap A above).
- [ ] Add R13/R14/R15 to `12-risk-register.md`.

This week (Days 1-3 of build):

- [ ] Reproduce the baseline; emit `baseline-result.json`.
- [ ] Build deterministic spec grid → 50 valid specs.
- [ ] Build deterministic verifier rules + invalid-spec fixtures → demonstrate ≥3 rejections.
- [ ] First batched-bootstrap CPU-vs-MI300X benchmark → emit `benchmark.json` per `09-gpu-and-benchmark-contract.md` schema. Headline target ≥10x; honest report whatever it is.

Before app implementation (Days 3-4):

- [ ] Run `18-user-validation-plan.md` with one real reviewer/methods PhD. Save `user-validation-notes.md`.
- [ ] Quote one pain anchor from that conversation in the slide deck (closes R15).

Before any build-in-public post (Days 4-5):

- [ ] Confirm baseline + benchmark artifacts both exist on disk.
- [ ] Run `14-quality-lint.md` § Text Lint to confirm no replication/proof/truth wording.
- [ ] Then post Update 1 ("Why one p-value is not enough"), then Update 2 ("MI300X benchmark") only after benchmark JSON is signed off.

---

## Part 6 — One-Page Executive Summary (for non-technical reviewers)

```text
Product:         SpecCurve — GPU-scale specification-robustness analysis.
                 Pick one public paper. Generate 200+ defensible variants
                 of its analysis. Reject the invalid ones. Run the rest
                 on AMD MI300X. Show whether the result holds.

User:            Statistically literate journal reviewer / methods instructor.

Hackathon fit:   All four LabLab criteria (Application of Technology,
                 Presentation, Business Value, Originality) mapped 1:1
                 to specific demo artifacts.

Differentiation: Not a paper chatbot, not replication, not truth verdict.
                 The verifier rejection beat is the visible proof that
                 agents are doing real work, not theater.

Wiki maturity:   Iterated 3x under product-lens (7.1 → 8.1 → 8.35).
                 Built on a schema-first knowledge framework (rohitg00
                 LLM Wiki v2). 7.0/10 adoption — high on structure,
                 intentionally low on scale features irrelevant for 7 days.

Single blocker:  Final paper/dataset/claim selection. The wiki refuses
                 to invent it, which is correct. Until selected,
                 implementation is blocked. After selected, every
                 downstream gate has a contract ready to consume.

Recommendation:  GO. Lock the dataset today.
```

---

## Closing Meta-Observation

The most striking thing about this wiki is that **it taught itself what to be**. V1's product-lens review identified five concrete gaps; V2 closed four and identified two new ones; V3 closed both and identified one (dataset). The wiki is not just a knowledge base — it is the team's *reasoning loop*. That is exactly the gist's `crystallization` capability operating without a name. The team did not need to label it; they just did it.

If the only thing the team takes from this brief is one sentence, it should be:

```text
The wiki is done arguing with itself. Pick the dataset and start building.
```
