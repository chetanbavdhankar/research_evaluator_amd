# Eval Gates

Run gates in order. Do not proceed to a downstream feature if the upstream evidence artifact is missing.

Live gate status is compiled in `gate-status.md`. This page defines gate contracts; `gate-status.md` records the current pass, blocked, or not-started state.

| Gate | Pass criteria | Fail action | Evidence artifact |
|---|---|---|---|
| Dataset gate | Dataset is public, citable, licensed, locally frozen, documented, and tied to one narrow claim. | Pick a different dataset. | `data/metadata.json`, citation, local file hash. |
| Baseline gate | Baseline runs deterministically; sample size/effect/uncertainty/statistic are saved; deviations documented. | Fix baseline or switch dataset. Do not start agents. | `baseline-result.json`, baseline notes. |
| Specification gate | At least 50 valid early specs; path to 200+ final specs; JSON schema valid; rationales present. | Narrow claim or choose richer dataset. | `spec-space.json`, schema validation log. |
| Verifier gate | Deterministic rules catch hard invalid specs; agent returns strict JSON; rejected specs do not execute. | Use deterministic-only verifier until agent is reliable. | `verifier-log.json`, invalid-spec fixtures. |
| AMD gate | MI300X detected; fair CPU/GPU benchmark runs same workload; tolerance passes; runtime and speedup logged. | Redesign numerical core or stop making AMD load-bearing claims. | `benchmark.json`, hardware log. |
| Robustness surface gate | Baseline highlighted; approved specs plotted; rejected specs visible; summary matches result table. | Simplify plot before adding charts. | Screenshot, surface data JSON. |
| User-value gate | One target reviewer/methods user can explain the report conclusion in under two minutes and says whether they would use it in review or teaching. | Revise report, wording, or surface before app polish. | `user-validation-notes.md` or interview summary. |
| Demo gate | Two-minute script works: paper/claim, baseline, specs, rejection, MI300X run, surface, cautious conclusion. | Cut scope until it fits. | Demo rehearsal video or notes. |
| Distribution gate | Hugging Face Space is live or blocker is documented; two technical updates are drafted or posted; AMD/ROCm feedback note exists. | Use alternate public app URL only with documented blocker; cut social scope to the two required technical updates. | Space URL, social links/drafts, feedback note. |
| Submission gate | Official assets complete: project info, cover, video, slides, public repo, demo platform, app URL. | Do not submit until missing asset is produced. | Submission checklist with links. |

## Daily Gate Questions

At the end of each build session, answer:

```text
What can we show a judge right now?
What evidence did we produce today?
What is still mocked, cached, unverified, or uncertain?
What wording would embarrass us in Q&A?
What wiki decision or contract changed?
```

## Gate Status Template

```yaml
gate_id:
status: pass | fail | blocked | not_started
evidence_artifact:
confidence:
source:
last_verified:
notes:
next_action:
```
