# Product Lens Review V3

> REVIEW/SOURCE PAGE - DO NOT BUILD DIRECTLY FROM THIS FILE.
> Current implementation authority lives in the control pages and `gate-status.md`.

Skill used: `ecc:product-lens`

Review target:

```text
speccurve-wiki/
speccurve-kickoff/
```

Review date:

```text
2026-05-05
```

Official hackathon page checked:

```text
https://lablab.ai/ai-hackathons/amd-developer
```

The official page still supports the core assumptions:

- Build AI agents and high-performance AI apps on AMD GPUs in the cloud.
- AMD AI Developer Cloud, ROCm, and model APIs are relevant technology.
- AMD Instinct MI300X access and $100 AMD Developer Cloud credits are listed.
- Judging criteria are Application of Technology, Presentation, Business Value, and Originality.
- Submission asks for project info, cover image, video, slide presentation, public GitHub repo, demo application platform, and application URL.
- Hugging Face Spaces and build-in-public updates are meaningful submission/distribution signals.

## Verdict

```text
GO for deterministic spine implementation after final dataset/claim selection.
NOT GO for full app implementation yet.
```

The latest wiki update resolves two important V2 gaps:

1. It adds a concrete user-validation plan.
2. It selects batched bootstrap as the first GPU prototype operation.

The biggest remaining blocker is now singular and clean:

```text
No final paper/dataset/claim is selected.
```

The wiki is no longer the bottleneck. Dataset selection is.

## Updated Product Diagnostic

### 1. Who Is This For?

Current answer:

```text
A statistically literate journal reviewer or methods instructor who wants to inspect whether a public-paper result depends on analysis choices.
```

Assessment:

```text
Strong and now supported by a validation plan.
```

The new `18-user-validation-plan.md` is the right lightweight move. It turns the first user from a plausible persona into a testable assumption.

Important nuance:

If Berkeley is used for the mock, validation proves the story is legible. It does not prove the final dataset/report is useful. Once the final dataset is chosen, repeat validation with the real report if time allows.

Score:

```text
8.5/10
```

### 2. What Is The Pain?

Current answer:

```text
Manual robustness checking is slow and fragmented; reviewers skip it because it requires writing many scripts for one result.
```

Assessment:

```text
Good enough for hackathon. Still qualitative, but now tied to a reviewer-grade report.
```

The before/after table in `01-product-thesis.md` is useful:

```text
Before: one baseline result plus manual scripts.
After: 200+ verified specs, rejected invalid specs, GPU benchmark, robustness surface, exportable report.
```

Score:

```text
7.5/10
```

### 3. Why Now?

Current answer:

```text
LLMs propose and explain structured analysis plans; deterministic code computes; AMD MI300X runs batched bootstrap/resampling/specification work.
```

Assessment:

```text
Stronger than V2 because the first GPU operation is now selected.
```

The first-operation decision is sound:

```text
batched bootstrap resampling for effect-size uncertainty across approved specs
```

Why it works:

- It creates honest parallel work even for moderate datasets.
- It produces uncertainty intervals reviewers understand.
- It is less claim-specific than permutation testing.
- It can be benchmarked fairly on CPU and GPU.

Remaining risk:

If the final dataset is tiny or the effect-size computation is too simple, the GPU story may still feel synthetic. Dataset selection must explicitly score "GPU workload quality."

Score:

```text
8/10 conceptually, 6/10 until benchmark artifact exists
```

### 4. What Is The 10-Star Version?

Current answer remains strong:

```text
DOI + public data link -> verified robustness report -> GPU-scale sensitivity checks -> exportable peer-review appendix.
```

Assessment:

```text
Strong. It gives direction without polluting the MVP.
```

Score:

```text
8/10
```

### 5. What Is The MVP?

Current MVP:

```text
One paper, one dataset, one claim, baseline, 200+ specs, invalid-spec rejection, fair CPU-vs-MI300X benchmark, robustness surface, Markdown/JSON report.
```

Assessment:

```text
Strong and buildable, once the dataset is selected.
```

MVP sequence is now product-correct:

```text
validation mock -> dataset decision -> baseline -> specs -> verifier -> GPU benchmark -> surface -> report -> app shell
```

Score:

```text
9/10
```

### 6. What Is The Anti-Goal?

Current anti-goals are excellent:

- No arbitrary upload.
- No fine-tuning.
- No general paper chatbot.
- No statistical IDE.
- No automatic causal-inference engine.
- No truth/fraud/replication verdict.
- No undisclosed cached run.

Assessment:

```text
This is one of the strongest parts of the product.
```

Score:

```text
9/10
```

### 7. How Do We Know It Is Working?

Current answer:

- Eval gates.
- User-value gate.
- Benchmark fairness contract.
- Demo gate.
- Quality lint.

Assessment:

```text
Strong. The wiki now has both engineering proof and user-value proof.
```

Remaining missing proof:

```text
No actual user-validation notes yet.
No actual dataset decision yet.
No actual benchmark artifact yet.
```

Score:

```text
8.5/10 as a plan, 0/10 as evidence until artifacts exist
```

## Scorecard

Hackathon-readiness score, not long-term company score.

| Dimension | V2 | V3 | Notes |
|---|---:|---:|---|
| Product clarity | 9 | 9 | Stable and clear. |
| First-user specificity | 8 | 8.5 | Validation plan added. |
| Pain clarity | 7 | 7.5 | Better before/after framing. |
| MVP discipline | 9 | 9 | Still strong. |
| AMD load-bearing story | 8 | 8.5 | First GPU operation selected. |
| Agentic differentiation | 8 | 8 | Verifier remains the strongest agentic beat. |
| Demo legibility | 8 | 8 | Good sequence; final dataset determines visual strength. |
| Business value | 7 | 7.5 | Report export + validation plan help. |
| Originality | 8 | 8 | Still defensible; prior-art acknowledgement remains important. |
| Q&A defensibility | 9 | 9 | Strong anti-overclaiming. |

Overall:

```text
8.35/10 as a hackathon product plan.
```

Potential after final dataset + baseline + benchmark:

```text
9/10.
```

## What Improved Since V2

### Improvement 1 - User-Value Gate Added

`18-user-validation-plan.md` is the right size. It does not overcomplicate research. It asks one target-type user whether the report is useful, honest, and trustworthy.

This closes the previous "user value is assumed" gap at the planning level.

### Improvement 2 - First GPU Operation Selected

`D-007` and `09-gpu-and-benchmark-contract.md` now specify batched bootstrap as the first MI300X prototype.

This makes the AMD work less vague.

### Improvement 3 - Superseded Files Are Safer

Old files now include a visible:

```text
SUPERSEDED SOURCE PAGE - DO NOT BUILD FROM THIS FILE
```

This reduces LLM drift if an agent reads broad file globs.

### Improvement 4 - Build Sequence Is Better

`16-build-sequence.md` now starts with:

```text
product wording -> validation mock -> dataset selection -> baseline
```

That is product-correct. It avoids building UI around an unproven claim.

## Remaining Gaps

### Gap 1 - Final Dataset Still Not Selected

This is now the only major blocker.

The decision template exists:

```text
speccurve-wiki/decisions/0001-final-dataset-and-claim.md
```

But it is explicitly a template. Until filled, implementation should not assume:

- paper
- dataset
- target claim
- outcome
- predictor
- baseline
- specification dimensions
- GPU workload quality

### Gap 2 - User Validation Is Planned But Not Run

The plan is good. It has not produced evidence.

Minimum acceptable evidence:

```text
speccurve-wiki/user-validation-notes.md
```

This can be lightweight: date, respondent type, artifact shown, answers, distrust triggers, decision impact.

### Gap 3 - Build-In-Public / Hugging Face Strategy Is Underused

The official page emphasizes Hugging Face Spaces and build-in-public updates. The wiki includes submission assets, but the product plan should use this as a winning tactic.

Recommended new artifact:

```text
speccurve-wiki/19-distribution-and-build-in-public-plan.md
```

Include:

- Hugging Face Space as preferred demo platform unless a blocker appears.
- Two technical updates:
  - Update 1: "Why one p-value is not enough; SpecCurve design."
  - Update 2: "MI300X benchmark: batched bootstrap robustness surface."
- Tags/accounts required by the official page.
- A short feedback note on AMD Developer Cloud/ROCm experience.

### Gap 4 - Dataset Selection Needs A Scoring Rubric

The decision template is useful, but selection will be faster with a scoring table.

Add to the decision template:

| Criterion | Weight |
|---|---:|
| Baseline reproducibility | 5 |
| Clean public data/license | 5 |
| Demo legibility | 5 |
| Meaningful spec dimensions | 5 |
| GPU workload quality | 5 |
| Low ethical/legal risk | 4 |
| Time to implement | 4 |
| Reviewer relevance | 3 |

This prevents the team from choosing a dataset that is interesting but unusable.

## Feature Prioritization

Updated ICE score.

| Work item | Impact | Confidence | Effort | ICE | Priority |
|---|---:|---:|---:|---:|---|
| Final paper/dataset/claim selection | 5 | 5 | 2 | 12.5 | P0 |
| One-page user-validation mock | 4 | 5 | 1 | 20.0 | P0 |
| Baseline reproduction | 5 | 4 | 3 | 6.7 | P0 |
| Batched bootstrap CPU/GPU prototype | 5 | 4 | 4 | 5.0 | P0 |
| Deterministic verifier fixtures | 4 | 5 | 2 | 10.0 | P0 |
| Dataset scoring rubric | 4 | 5 | 1 | 20.0 | P0 |
| Robustness surface from fixed JSON | 5 | 4 | 3 | 6.7 | P1 |
| Exportable Markdown report | 4 | 4 | 2 | 8.0 | P1 |
| Hugging Face/build-in-public plan | 3 | 5 | 1 | 15.0 | P1 |
| Proposer LLM agent | 3 | 3 | 3 | 3.0 | P2 |
| Explainer LLM agent | 3 | 4 | 2 | 6.0 | P2 |
| Full app shell | 4 | 3 | 4 | 3.0 | P2 |
| Arbitrary upload | 2 | 2 | 5 | 0.8 | Do not build |

## Go / No-Go Recommendation

### Go Now

Proceed with:

1. Dataset scoring rubric.
2. One-page user-validation mock.
3. Final paper/dataset/claim selection.
4. Baseline reproduction.
5. Batched bootstrap CPU/GPU prototype.
6. Deterministic verifier fixtures.

### Not Yet Go

Do not start:

- Full app shell.
- Arbitrary upload.
- Multi-paper workflow.
- Fine-tuning.
- Broad LLM paper assistant features.

## Product-Lens Bottom Line

The product direction is now strong. The wiki is no longer the core problem.

The current state is:

```text
World-class plan, no selected scientific object yet.
```

The next move should be brutally practical:

```text
Score 3-5 candidate papers/datasets, select one, reproduce the baseline, and run the first batched-bootstrap benchmark.
```

That will convert SpecCurve from a rigorous concept into a credible hackathon product.
