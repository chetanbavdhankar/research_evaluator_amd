# Gate Status

This page is the live compiled status for `10-eval-gates.md`. Update it when an evidence artifact is created, rejected, or explicitly deferred.

Metadata:

```yaml
confidence: high
source: speccurve-wiki/10-eval-gates.md; current filesystem check
last_verified: 2026-05-05
status: active
```

| Gate | Status | Evidence artifact | Confidence | Notes | Next action |
|---|---|---|---|---|---|
| Dataset gate | blocked | `decisions/0001-final-dataset-and-claim.md` is still a template | high | Final paper, dataset, and claim are not locked. | Score 3-5 candidates and fill the decision record. |
| Baseline gate | blocked | none | high | Baseline depends on the final dataset and claim. | Build deterministic baseline after dataset gate. |
| Specification gate | blocked | none | medium | Spec dimensions depend on the final claim and dataset schema. | Generate rule-based spec grid after baseline. |
| Verifier gate | blocked | none | medium | Verifier fixtures depend on the spec schema. | Add deterministic invalid-spec fixtures after spec grid. |
| AMD gate | blocked | none | high | No `benchmark.json` or hardware log exists yet. | Run first fair CPU-vs-MI300X batched-bootstrap benchmark. |
| Robustness surface gate | blocked | none | medium | Surface depends on approved spec results and baseline marker. | Build after result table exists. |
| User-value gate | blocked | `user-validation-notes.md` opened, no completed reviewer evidence | high | Evidence log exists only as a blocked placeholder. | Run `18-user-validation-plan.md` after mock or real report. |
| Demo gate | not_started | none | medium | Demo depends on upstream evidence gates. | Rehearse only after core artifacts exist. |
| Distribution gate | not_started | none | medium | Hugging Face Space is preferred, but not yet validated. | Document blocker or publish Space after app/demo path exists. |
| Submission gate | not_started | none | medium | Submission assets depend on demo and distribution gates. | Prepare after demo rehearsal passes. |

## Current Build Readiness

```text
GO: implementation planning and deterministic-spine work after dataset selection.
NOT GO: full app shell, public claims, build-in-public posts, or submission assets.
P0 blocker: final dataset/paper/claim decision.
```
