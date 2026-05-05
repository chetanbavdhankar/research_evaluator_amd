# SpecCurve Wiki

This wiki is the control system for building SpecCurve. Read it before coding, update it after decisions, and treat unsourced claims as draft until they pass the quality lint.

## Core Product

SpecCurve performs GPU-scale specification robustness analysis. For one selected public paper, public dataset, and target claim, it generates a reviewer-grade robustness report with verifier-checked specifications and AMD MI300X batch execution. The output is a robustness surface, not a truth verdict.

## Non-Negotiable Framing

Use:

```text
GPU-scale specification robustness analysis.
```

Avoid:

```text
We replicated the paper.
We proved the paper wrong.
We solved the replication crisis.
```

SpecCurve does not collect independent new data and does not prove a paper true or false. It analyzes robustness across defensible specifications on existing public data.

## Recommended Reading Order

1. `00-operating-manual.md`
2. `01-product-thesis.md`
3. `02-hackathon-judging-map.md`
4. `04-knowledge-schema.md`
5. `05-entity-graph.md`
6. `06-feature-contracts.md`
7. `07-agent-contracts.md`
8. `08-data-and-claim-contract.md`
9. `09-gpu-and-benchmark-contract.md`
10. `10-eval-gates.md`
11. `11-demo-contract.md`
12. `12-risk-register.md`
13. `13-decision-log.md`
14. `16-build-sequence.md`
15. `18-user-validation-plan.md`
16. `user-validation-notes.md`
17. `19-distribution-and-build-in-public-plan.md`
18. `19-product-lens-review-v3.md`
19. `20-product-lens-brief.md`
20. `gate-status.md`

Use `index.md` for the full catalog, `03-source-map.md` to trace where claims came from, and `gate-status.md` for the live readiness state.

## Authority Rule

The top-level control pages are the current implementation authority. `19-product-lens-review-v3.md` and `20-product-lens-brief.md` are review/source artifacts, not build contracts. Archived pages under `archive/` are traceability only and must not be treated as active unless a current control page and `13-decision-log.md` promote the claim.

## Readiness State

The wiki is GO for implementation planning. It is not yet GO for full app implementation until these blockers are resolved:

- Final paper/dataset/claim decision is logged.
- Baseline gate passes.
- First MI300X batch operation is prototyped against a fair CPU comparison.
- One lightweight target-user validation check is completed or explicitly deferred.

See `gate-status.md` for the current compiled status of these blockers.

## How To Use This Wiki

- Before building: read the relevant contract page and the linked decision records.
- During building: keep deterministic code responsible for statistics and benchmarks; keep LLMs responsible for structured proposals, verification explanations, and cautious summaries.
- After building: update facts, decisions, open questions, confidence, status, and evidence artifacts.
- Before demo or submission: run the checks in `14-quality-lint.md`.

If a claim is not sourced, not verified, or contradicts a newer decision, do not build from it.
