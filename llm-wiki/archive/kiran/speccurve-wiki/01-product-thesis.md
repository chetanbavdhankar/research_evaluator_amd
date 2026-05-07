# Product Thesis

## One-Sentence Product

SpecCurve generates a reviewer-grade robustness report for one public research claim by verifying defensible analysis specifications and executing the approved batch on AMD MI300X.

Metadata:

```yaml
confidence: high
source: speccurve-kickoff/README.md; speccurve-wiki/19-product-lens-review-v3.md; speccurve-wiki/20-product-lens-brief.md
last_verified: 2026-05-05
status: active
decision_id_optional: D-001
```

## First User

A statistically literate journal reviewer or methods instructor who wants to inspect whether a public-paper result depends on analysis choices.

Why this user:

- They already understand covariates, exclusions, model families, and sensitivity analysis.
- They can evaluate a robustness report without enterprise deployment.
- They have a concrete workflow: attach a robustness appendix to review, teaching, or public critique.

## Pain

Manual robustness checking is slow and fragmented. A reviewer may spend hours or days writing scripts for alternate covariates, exclusions, models, transformations, and resampling checks. Most reviewers skip this because it is too much work for one result.

Before/after proof for the MVP:

| Before SpecCurve | After SpecCurve |
|---|---|
| One baseline result plus manual scripts. | 200+ verified specs, rejected invalid specs, GPU benchmark, robustness surface, and exportable report. |

## Why Now

LLMs can now propose and explain structured analysis plans, but should not compute the statistics. AMD MI300X can run large batched regressions, bootstraps, permutation tests, and specification sweeps fast enough to make the robustness report interactive.

## Ten-Star Version

A reviewer provides a paper DOI and public data link. SpecCurve extracts the target claim, builds a verified specification space, runs GPU-scale sensitivity checks, shows an interactive robustness surface, and exports a peer-review appendix with code, provenance, benchmark logs, and limitations.

## Hackathon MVP

For one selected public paper:

- Freeze one public dataset locally.
- Define one target claim.
- Reproduce or approximate one baseline result.
- Generate 200+ candidate specifications, with at least 50 valid specs early.
- Reject at least three intentionally invalid specifications before execution.
- Run a fair CPU-vs-MI300X batch benchmark.
- Show a robustness surface with baseline marker, approved specs, rejected specs, and cautious conclusion.
- Export a Markdown or JSON robustness report.

## User-Value Metric

At least one target reviewer, methods PhD, statistician, or research instructor should see a one-page mock report and be able to:

- Explain the robustness conclusion in under two minutes.
- Say whether they would use it in review or teaching.
- Identify what would make them distrust it.
- Flag any wording that feels scientifically dishonest.

## Anti-Goals

- No arbitrary paper upload for MVP.
- No arbitrary dataset upload for MVP.
- No fine-tuning.
- No general paper chatbot.
- No statistical IDE.
- No automatic causal-inference engine.
- No fraud, misconduct, truth, or replication verdict.
- No hidden cached run presented as live.

## Go / No-Go Rule

Go only if the team can lock a dataset and claim, reproduce a baseline, generate defensible specs, reject invalid specs, and measure a real MI300X workload on comparable CPU/GPU work.

No-go or pivot if the GPU path is decorative, the dataset cannot support a defensible baseline, or the demo wording requires walking back "replication."
