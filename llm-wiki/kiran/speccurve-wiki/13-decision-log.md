# Decision Log

Decision status values follow `04-knowledge-schema.md`: `active`, `superseded`, `uncertain`, or `rejected`.

## Active Decisions

### D-001 - Frame Product As Specification Robustness, Not Replication

```yaml
status: active
decision: Use "GPU-scale specification robustness analysis" as the product framing.
rationale: SpecCurve uses existing public data and does not collect independent new data, so replication framing overclaims.
supersedes: SD-001, SD-002
confidence: high
source: speccurve-kickoff/README.md; brainstorm/codex-review/SYNTHESIS-DELTA.md
last_verified: 2026-05-05
```

### D-002 - Winning Wedge

```yaml
status: active
decision: "For one public paper, generate a reviewer-grade robustness report with verifier-checked specifications and MI300X batch execution."
rationale: This is narrow, demoable, judge-legible, and defensible for a 3-person hackathon team.
supersedes: broad AI-for-research and replication-crisis framings
confidence: high
source: speccurve-wiki/19-product-lens-review-v3.md; speccurve-wiki/20-product-lens-brief.md; user prompt
last_verified: 2026-05-05
```

### D-003 - MVP Scope Is One Paper, One Dataset, One Claim

```yaml
status: active
decision: Do not build arbitrary upload or multi-paper workflows before the MVP is proven.
rationale: The product wins by depth and auditability, not breadth.
confidence: high
source: speccurve-kickoff/02-product-requirements.md
last_verified: 2026-05-05
```

### D-004 - LLMs Do Not Compute Statistics

```yaml
status: active
decision: LLMs propose, verify, explain, and write reports; deterministic code computes all statistics and benchmarks.
rationale: Keeps results auditable and prevents hallucinated numbers.
confidence: high
source: speccurve-kickoff/03-technical-runbook.md; speccurve-wiki/00-operating-manual.md; speccurve-wiki/07-agent-contracts.md
last_verified: 2026-05-05
```

### D-005 - AMD Claim Requires Fair Benchmark Evidence

```yaml
status: active
decision: MI300X is load-bearing only when the same data/specs/resampling count run on CPU and GPU, outputs match within tolerance, and hardware/runtime are logged.
rationale: Prevents decorative GPU use and challenged speedup claims.
confidence: high
source: speccurve-wiki/09-gpu-and-benchmark-contract.md; speccurve-kickoff/03-technical-runbook.md
last_verified: 2026-05-05
```

### D-006 - Final Dataset Is Not Yet Selected

```yaml
status: uncertain
decision: No final paper, dataset, or target claim is locked.
rationale: The wiki must provide criteria and templates rather than inventing a final dataset.
confidence: high
source: speccurve-kickoff/09-data-selection-checklist.md; user prompt
last_verified: 2026-05-05
```

### D-007 - First GPU Prototype Operation Is Batched Bootstrap

```yaml
status: active
decision: Prototype the first MI300X workload as batched bootstrap resampling for effect-size uncertainty across approved specifications.
rationale: Batched bootstrap creates honest parallel work for moderate-sized datasets, supports reviewer-facing uncertainty, and remains broadly applicable before the final claim shape is locked. Permutation tests are a second operation when exchangeability is valid for the selected claim.
confidence: medium
source: speccurve-wiki/archive/17-product-lens-review-v2.md; speccurve-kickoff/03-technical-runbook.md
last_verified: 2026-05-05
```

### D-008 - Wiki Is Planning-Ready, Not App-Implementation-Ready

```yaml
status: active
decision: Treat the wiki as ready for implementation planning, but block full app implementation until dataset/claim, baseline, first GPU prototype, and user-value validation are resolved.
rationale: The remaining blockers are product-proof gates, not documentation gaps.
confidence: high
source: speccurve-wiki/README.md; speccurve-wiki/gate-status.md
last_verified: 2026-05-05
```

### D-009 - Hugging Face Space Is Preferred Demo Platform

```yaml
status: active
decision: Use Hugging Face Space as the preferred demo platform and app URL unless a documented blocker appears.
rationale: The official hackathon page positions Hugging Face as the deployment layer, asks teams to publish the project as a Space and submit the Space link, and includes a Hugging Face special prize tied to Space likes.
confidence: high
source: https://lablab.ai/ai-hackathons/amd-developer; speccurve-wiki/19-distribution-and-build-in-public-plan.md
last_verified: 2026-05-05
```

## Superseded Or Rejected Decisions

### SD-001 - Original BinderForge Primary Recommendation

```yaml
status: superseded
old_decision: Build original BinderForge-style biology demo as primary.
superseded_by: D-002
reason: Later Codex review found tool-stack, ROCm, docking-score, and domain-validity risks. SpecCurve is now the active product.
confidence: high
source: brainstorm/codex-review/codex-meta-review.md; brainstorm/codex-review/SYNTHESIS-DELTA.md
last_verified: 2026-05-05
directive: BinderForge is rejected as the current build lane, not paused as a fallback. If SpecCurve stalls, repair dataset, baseline, or benchmark gates before reconsidering product direction.
```

### SD-002 - ReplicaCheck / Replication Framing

```yaml
status: superseded
old_decision: Present the product as replication or ReplicaCheck.
superseded_by: D-001
reason: The product uses existing public data. "SpecCurve" and specification robustness analysis are more accurate.
confidence: high
source: brainstorm/codex-review/SYNTHESIS-DELTA.md
last_verified: 2026-05-05
```

### SD-003 - Proving A Paper Right Or Wrong

```yaml
status: rejected
old_decision: Use the tool to prove a paper true, false, fraudulent, or solved.
superseded_by: D-001
reason: SpecCurve maps robustness under a defined specification space; it does not adjudicate truth.
confidence: high
source: speccurve-kickoff/01-plain-language-explainer.md
last_verified: 2026-05-05
```

### SD-004 - Berkeley Admissions As Final AMD Proof

```yaml
status: superseded
old_decision: Treat Berkeley admissions as the final GPU proof dataset.
superseded_by: D-006
reason: Berkeley is excellent as a teaching example but small; final GPU proof needs a selected dataset or disclosed resampling workload.
confidence: high
source: speccurve-kickoff/10-example-berkeley-paper-walkthrough.md; speccurve-wiki/08-data-and-claim-contract.md
last_verified: 2026-05-05
```

## Open Questions

| ID | Question | Needed before | Status |
|---|---|---|---|
| OQ-001 | What final paper/dataset/claim will be used? | Baseline implementation | open |
| OQ-002 | Does the final dataset/claim require replacing bootstrap-first with a permutation-first kernel? | AMD gate | open |
| OQ-003 | Is there any blocker to using Hugging Face Space as the submitted app URL? | Submission gate | open |
| OQ-004 | Which model endpoint handles proposer/verifier/explainer calls, and what is the offline fallback? | Agent integration | open |
