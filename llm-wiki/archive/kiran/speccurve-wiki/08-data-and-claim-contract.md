# Data And Claim Contract

The final dataset, paper, and claim are not selected. Do not invent them. Use this contract to select them.

## Dataset Selection Rules

A final dataset must:

- Be public and citable.
- Have clear reuse permission or license.
- Be downloadable and frozen locally.
- Have documentation or a codebook.
- Support one narrow target claim.
- Be clean enough to load quickly.
- Have meaningful specification dimensions.
- Support enough rows, variables, or resampling for an honest GPU batch workload.
- Avoid high-liability medical, private, scraped, or unclear-license data.

Prefer:

- OSF datasets with clean CSV/parquet files.
- Many Labs style public datasets.
- Psychological Science Accelerator or ManyBabies public datasets.
- Education or behavioral datasets with documented analysis choices.
- Methods-teaching benchmark datasets.

## Claim Selection Rules

A target claim must:

- Identify one outcome.
- Identify one predictor/treatment/exposure.
- Define expected direction or measurable effect.
- Be testable with the available data.
- Be narrow enough for a two-minute demo.
- Avoid legal, clinical, or misconduct conclusions.
- State what it does not prove.

Good shape:

```text
The study reports that X is associated with Y in dataset Z.
```

Bad shape:

```text
This paper is wrong and SpecCurve proves it.
```

## Required Baseline

Before agents or UI:

- Load the frozen dataset.
- Implement the baseline specification.
- Save sample size, effect size, uncertainty, p-value or statistic, runtime, and deviations from the source.
- If the baseline cannot be reproduced or explained in one day, choose another dataset.

## Berkeley Admissions Teaching Example

Berkeley graduate admissions is useful for explaining analysis sensitivity:

- Paper: Bickel, Hammel, and O'Connell, 1975.
- Dataset: `UCBAdmissions`.
- Teaching claim: "Does the apparent gender gap survive department-aware analysis?"
- Lesson: aggregate analysis and department-aware analysis can point to different conclusions.

Warning:

```text
Berkeley is weak as the final AMD proof because it is small. If used in a demo, the GPU relevance must come from disclosed batched bootstrap/permutation/specification sweeps, not from pretending the raw dataset is large.
```

## Final Dataset Decision Template

Add the filled version to `13-decision-log.md` or a dedicated decision page before implementation treats it as fixed.

```yaml
decision_id:
status: active | uncertain | rejected
dataset_name:
source_url:
license:
citation:
paper:
target_claim:
outcome:
predictor:
expected_direction:
rows:
columns:
baseline_spec:
baseline_reference:
specification_dimensions:
gpu_workload_plan:
why_good_for_demo:
why_good_for_gpu:
limitations:
rejected_alternatives:
confidence:
source:
last_verified:
```

## Dataset Scoring Rubric

Use this rubric before committing to a dataset. Score each criterion from 0 to 5, multiply by weight, and reject any dataset that triggers a kill condition even if the weighted score is high.

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

Detailed scoring fields live in `decisions/0001-final-dataset-and-claim.md`.

## Dataset Kill Conditions

Switch datasets if:

- License or citation is unclear.
- Data requires heavy cleaning.
- Claim cannot be stated in one sentence.
- Baseline cannot be reproduced or explained.
- There are not enough meaningful specification dimensions.
- GPU workload would be unrelated to the product.
- Subject matter creates avoidable sponsor or ethics risk.
