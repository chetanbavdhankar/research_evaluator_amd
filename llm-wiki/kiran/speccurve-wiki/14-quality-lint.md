# Quality Lint

Run this checklist before implementation, demo rehearsal, and final submission. It is a wiki lint, not a code lint.

## Required Checks

| Check | Fail condition | Fix |
|---|---|---|
| Orphan claims | Claim has no source or decision record. | Add source metadata or remove claim. |
| Missing sources | External fact lacks path/URL and last verified date. | Update `03-source-map.md` and local page metadata. |
| Stale assumptions | `uncertain` item is used as active implementation input. | Make a decision or keep it out of code. |
| Contradictions | Two active pages disagree. | Resolve in `13-decision-log.md`; mark older claim superseded. |
| Overclaiming | Any page says replication, proof, truth, fraud, solved crisis, or settled science. | Rewrite to specification robustness language. |
| Unsupported AMD claims | Speedup/MI300X statement lacks benchmark artifact. | Run AMD gate or mark claim uncertain. |
| Missing acceptance criteria | Feature contract lacks pass/fail criteria. | Update `06-feature-contracts.md`. |
| Missing confidence/status metadata | Durable claim has no confidence or status. | Add required metadata from `04-knowledge-schema.md`. |
| Agent overreach | Agent contract lets LLM compute statistics or override hard rules. | Tighten `07-agent-contracts.md`. |
| Demo drift | Demo includes features outside `11-demo-contract.md`. | Cut or defer feature. |
| Archive drift | Superseded or source-only page remains top-level and can be mistaken for a build contract. | Move it under `archive/` or promote the claim into a current top-level contract page and decision record. |
| Missing user proof | App implementation starts before user-value validation is completed or explicitly deferred. | Run `18-user-validation-plan.md` or record a deferral decision. |
| Distribution drift | Demo platform or social update plan ignores official Hugging Face/build-in-public surfaces without a recorded blocker. | Follow `19-distribution-and-build-in-public-plan.md` or update `13-decision-log.md`. |

## Text Lint

Search for unsafe language:

```bash
rg -n "replicated|replication crisis|\\bproved\\b|prove the paper|\\bfraud\\b|misconduct|truth verdict|\\bsolved\\b" speccurve-wiki --glob '!speccurve-wiki/archive/**'
```

Allowed mentions are only in forbidden-language lists, Q&A clarifications, or superseded decision records.

## Metadata Lint

For new or changed pages, check:

```text
confidence:
source:
last_verified:
status:
```

If a page intentionally contains templates without values, label them as templates and do not treat them as active decisions.

## AMD Lint

Before any AMD claim appears in README, video, slides, or app:

- Does the benchmark use the same data, specs, and resampling count?
- Does the tolerance check pass?
- Are hardware, ROCm/HIP/PyTorch versions logged?
- Is warmup policy stated?
- Is the speedup computed, not typed by hand?
- Does the UI distinguish precomputed robustness output from live benchmark evidence?

## User-Value Lint

Before full app implementation:

- Has a one-page mock or report been shown to a target reviewer/methods user?
- Can that person explain the conclusion in under two minutes?
- Did they flag any wording as scientifically dishonest?
- Are distrust triggers mapped to risks, feature contracts, or open questions?

## Distribution Lint

Before submission:

- Is Hugging Face Space the submitted app URL, or is the blocker documented?
- Do the two technical updates avoid unsupported benchmark or dataset claims?
- Does each update tag one LabLab account and one AMD account on the chosen platform?
- Is the AMD Developer Cloud/ROCm feedback note concrete and evidence-backed?
- Are public repo, Space, benchmark artifact, and limitations linked consistently?

## Final Submission Lint

Before submitting:

- Official criteria are still checked against LabLab page.
- Submission asset checklist is complete.
- Public repo has README, limitations, dataset citation, and benchmark method.
- Demo video follows the two-minute contract.
- Slide deck uses non-replication framing.
- App URL opens without private setup.
- Hugging Face Space link is included or blocker is recorded.
- Build-in-public technical update links are recorded if pursuing the extra challenge.
- AMD Developer Cloud/ROCm feedback note is ready.
- Backup path is disclosed.
