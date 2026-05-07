# Decision Template: Final Dataset And Claim

Status: template, not selected.

Use this file to lock the final paper, dataset, and target claim. Do not treat placeholders as active decisions.

```yaml
decision_id: D-DATASET-001
status: active | rejected | uncertain
dataset_name:
source_url:
license:
citation:
paper_title:
paper_url_or_doi:
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

## Acceptance Criteria

- Dataset is public, licensed, citable, and locally frozen.
- Claim is one sentence and does not imply truth, fraud, or replication.
- Baseline can be reproduced or explained.
- Specification dimensions can produce at least 50 early valid specs and a path to 200+ final specs.
- Dataset can support batched bootstrap work or a better documented MI300X workload.
- Limitations are clear enough for judge Q&A.

## Scoring Rubric

Use this rubric before selecting a dataset. Score each criterion from 0 to 5, multiply by weight, and prefer the highest total that also passes the kill conditions.

| Criterion | Weight | Score 0 means | Score 5 means |
|---|---:|---|---|
| Baseline reproducibility | 5 | No clear baseline or impossible to reproduce quickly. | Baseline is documented and reproducible or explainable in one day. |
| Clean public data/license | 5 | Data is private, unclear-license, messy, or hard to fetch. | Data is public, citable, licensed, documented, and easy to freeze locally. |
| Demo legibility | 5 | Claim needs long domain/statistics explanation. | A judge understands the paper, claim, and result shape in under 30 seconds. |
| Meaningful spec dimensions | 5 | Few defensible choices; surface will be flat or arbitrary. | Multiple real covariate, exclusion, model, transform, and resampling choices. |
| GPU workload quality | 5 | GPU work is unrelated or synthetic. | Batched bootstrap/permutation/spec sweeps are honest and load-bearing. |
| Low ethical/legal risk | 4 | Subject invites legal, medical, misconduct, or sensitive-group overclaiming. | Subject is safe for a public sponsor demo with cautious wording. |
| Time to implement | 4 | Heavy cleaning or domain modeling blocks the hackathon timeline. | Loader, baseline, specs, and first benchmark are plausible quickly. |
| Reviewer relevance | 3 | Output is only interesting as a toy example. | A reviewer or methods instructor would plausibly inspect or teach from it. |

```yaml
scoring:
  baseline_reproducibility:
    weight: 5
    score:
    notes:
  clean_public_data_license:
    weight: 5
    score:
    notes:
  demo_legibility:
    weight: 5
    score:
    notes:
  meaningful_spec_dimensions:
    weight: 5
    score:
    notes:
  gpu_workload_quality:
    weight: 5
    score:
    notes:
  low_ethical_legal_risk:
    weight: 4
    score:
    notes:
  time_to_implement:
    weight: 4
    score:
    notes:
  reviewer_relevance:
    weight: 3
    score:
    notes:
  weighted_total:
```

## Decision Notes

Fill this section after selection:

```text
Chosen dataset:
Chosen claim:
Rejected alternatives:
Why this is the right hackathon demo:
Known risks:
Next gate:
```
