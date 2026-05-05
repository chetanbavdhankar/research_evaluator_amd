# Risk Register

| ID | Category | Risk | Severity | Likelihood | Mitigation | Kill condition |
|---|---|---|---|---|---|---|
| R01 | Product | SpecCurve is mistaken for replication. | high | medium | Ban replication wording; Q&A answer in demo; report limitations. | Public copy requires walking back "replication." |
| R02 | Technical | MI300X is decorative because stats run in CPU loops. | high | medium | Tensorize one core workload; show fair benchmark and logs. | No real GPU-backed speedup after AMD gate. |
| R03 | Statistical | Baseline cannot be reproduced or explained. | high | medium | Baseline gate before agents/UI; document deviations. | Baseline unresolved after one focused build day. |
| R04 | Data | Dataset license, citation, or documentation is unclear. | high | low-medium | Use public/citable datasets; freeze locally; record license. | License or provenance remains unclear. |
| R05 | Demo | Live GPU/model endpoint fails. | medium | medium | Precomputed run with disclosure; live mini-benchmark; backup video. | No honest fallback path. |
| R06 | Judging | Demo looks like a paper chatbot. | high | medium | Center verifier rejection, AMD panel, surface, report export. | Agents only produce prose. |
| R07 | Visualization | Robustness surface is flat or confusing. | medium | medium | Choose claim with meaningful spec dimensions; simplify axes; highlight baseline. | Judge cannot explain the plot after 30 seconds. |
| R08 | Benchmark | CPU/GPU comparison is unfair or numerically inconsistent. | high | medium | Follow `09-gpu-and-benchmark-contract.md`. | Tolerance check fails or workloads differ. |
| R09 | Scope | Team builds arbitrary uploads, auth, SaaS, or too many datasets. | high | medium | One paper/dataset/claim until MVP gates pass. | MVP no longer fits two-minute demo. |
| R10 | Ethical | Product implies misconduct, fraud, discrimination, or causal truth beyond data. | high | low-medium | Use cautious claim language and explicit limitations. | Conclusion asserts truth/fraud/causality without design support. |
| R11 | Business | User and value are too abstract. | medium | medium | Anchor to reviewer/methods instructor and exportable report. | Submission says "for all researchers" without concrete workflow. |
| R12 | Agent | Verifier approves invalid specs or proposer invents columns. | high | medium | Hard deterministic rules, fixtures, JSON schema, fallback. | Outcome leakage or missing-column spec reaches execution. |
| R13 | Distribution | Build-in-public work begins before product wording and evidence are locked, forcing public retraction. | medium | medium | Hold public updates until baseline gate passes; draft copy in repo and lint before posting. | Public update goes live before D-006 closes or baseline evidence exists. |
| R14 | Strategic | Team treats the superseded BinderForge direction as a paused backup and pivots back when SpecCurve gets hard. | medium | low-medium | Keep BinderForge explicitly superseded/rejected in `13-decision-log.md`; spend recovery effort on dataset or benchmark repair first. | Build energy returns to BinderForge after Day 3. |
| R15 | Business | Pain remains hypothetical because no target user has quantified manual robustness-check effort. | low | medium | Run `18-user-validation-plan.md`; capture one concrete pain anchor for the slide deck. | Submission narrative uses only hypothetical time-saved language. |

## Risk Review Rule

Update this register when:

- A dataset is selected.
- A benchmark is run.
- A cached/precomputed path is introduced.
- A public claim or submission asset is drafted.
- Any gate fails.
