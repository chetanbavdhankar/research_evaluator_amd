# Source Map

Use this page to trace claims. Confidence means confidence that the source accurately supports the wiki claim, not confidence that implementation will succeed.

## External Sources

| Source | What it contributes | Confidence | Status | Last verified |
|---|---|---:|---|---|
| https://lablab.ai/ai-hackathons/amd-developer | Official judging criteria, submission checklist, AMD Developer Cloud/ROCm/MI300X framing, credits, Hugging Face Space deployment guidance, build-in-public requirements, community tags, and event context. | high | active | 2026-05-05 |
| https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2 | LLM Wiki v2 patterns: raw sources + wiki + schema, confidence, supersession, graph relationships, lint, automation hooks, privacy/governance, crystallization, schema as product. | high | active | 2026-05-05 |

## Local Source Groups

| Source | What it contributes | Confidence | Status |
|---|---|---:|---|
| `speccurve-kickoff/README.md` | Product summary, non-replication framing, first technical GPU gate, recommended demo shape. | high | active source |
| `speccurve-kickoff/01-plain-language-explainer.md` | Judge-friendly explanation, agent/GPU/verifier load-bearing distinction, originality framing. | high | active source |
| `speccurve-kickoff/02-product-requirements.md` | MVP scope, functional requirements, non-goals, final demo target. | high | active source |
| `speccurve-kickoff/03-technical-runbook.md` | Architecture, data models, ROCm sanity check, GPU kernels, verifier rules, logging, done definition. | high | active source |
| `speccurve-kickoff/04-task-backlog.md` | Practical phase order from dataset to hardening. | high | active source |
| `speccurve-kickoff/05-demo-script.md` | Two-minute demo beats and Q&A language. | high | active source |
| `speccurve-kickoff/06-judging-alignment.md` | Prior mapping to LabLab criteria and submission summaries. | high | active source |
| `speccurve-kickoff/07-risk-register.md` | Existing product, GPU, dataset, visualization, agent, overclaim, demo, scope, business, and license risks. | high | active source |
| `speccurve-kickoff/08-submission-assets.md` | Submission copy blocks and asset checklist. | high | active source |
| `speccurve-kickoff/09-data-selection-checklist.md` | Dataset and claim selection criteria, kill conditions, final dataset package. | high | active source |
| `speccurve-kickoff/10-example-berkeley-paper-walkthrough.md` | Berkeley admissions teaching example and warning that it is weak as final GPU proof because it is small. | high | active source |
| `../brainstorm/codex-review/codex-meta-review.md` | Adversarial correction from BinderForge toward SpecCurve/ReplicaCheck, MI300X load-bearing condition, anti-replication framing, GPU-vectorized stats requirements. | high | active source |
| `../brainstorm/codex-review/SYNTHESIS-DELTA.md` | Supersession of earlier synthesis, product correction, team-depth decision tree, SpecCurve/Rebuilt ReplicaCheck direction. | high | active source |
| `speccurve-wiki/archive/17-product-lens-review-v2.md` | Second product-lens critique confirming the wiki upgrade and identifying remaining proof blockers: final dataset/claim, first GPU operation, user validation, endpoint/hosting choices, and superseded-file risk. | high | archived source review; superseded by `19-product-lens-review-v3.md` and complemented by `20-product-lens-brief.md` |
| `speccurve-wiki/19-product-lens-review-v3.md` | Latest full product-lens review after user-value, first GPU operation, and superseded-file safety improvements. | high | active source review |
| `speccurve-wiki/19-distribution-and-build-in-public-plan.md` | Distribution plan: Hugging Face Space default, two technical updates, required tags/accounts, and AMD Developer Cloud/ROCm feedback note. | high | active source |
| `speccurve-wiki/20-product-lens-brief.md` | Founder review, seven-question product diagnostic, LLM Wiki v2 adoption audit, and next-step checklist. | high | active source review |
| `speccurve-wiki/gate-status.md` | Live compiled gate status, current blockers, and next evidence action. | high | active control |
| `speccurve-wiki/user-validation-notes.md` | Live target-user validation evidence log; currently opened with no completed interview evidence. | high | active evidence log |

## Facts vs Decisions vs Assumptions

| Type | Examples | Handling |
|---|---|---|
| Fact | Official criteria, source file contents, current wiki file names. | Must cite source and last verification date. |
| Decision | SpecCurve name, non-replication framing, MVP one paper/dataset/claim, final dataset not selected. | Must appear in `13-decision-log.md`. |
| Assumption | Reviewer first user, 10x headline speedup threshold, final dataset likely from OSF/Many Labs category. | Mark `uncertain` until validated. |
| Open question | Final dataset, final paper/claim, live model endpoint, hosting platform. | Do not code as fixed until decided. |
