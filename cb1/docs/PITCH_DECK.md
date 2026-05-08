# Pitch Deck Outline

## 1. Title

SpecCurve L0: AMD MI300X Evidence Lab

One public dataset, many defensible analyses, one cautious robustness report.

## 2. Problem

Research readers often see one headline estimate and one confidence interval. For methods-heavy
claims, the actual question is whether the result survives reasonable choices about matching,
weighting, filters, covariates, transformations, and uncertainty.

## 3. Product

SpecCurve turns a public result into a deterministic robustness appendix:

- Freeze the dataset and source hashes.
- Lock one narrow claim.
- Generate a pre-declared specification grid.
- Reject invalid specs before execution.
- Compute the robustness surface.
- Export a report with provenance and limitations.

## 4. Demo Dataset

NBER Dehejia-Wahba NSW treated sample plus PSID controls.

- 185 treated rows.
- 2,490 control rows.
- 2,675 total rows.
- Outcome: 1978 real earnings, `re78`.
- Treatment: NSW training indicator, `treat`.
- Derived unemployment indicators: `u74`, `u75`.

## 5. Wiki C Implementation

The local build includes:

- 240 approved specs from a 768-spec deterministic grid.
- OLS and ridge outcome models.
- Propensity-score matching.
- IPW ATT weighting.
- Mahalanobis nearest-neighbor matching.
- Coarsened exact matching.
- Logit and probit propensity models.
- Support rules and sample filters.

## 6. Verifier

The verifier rejects:

- Claim mutation.
- Outcome leakage.
- Missing columns.
- Undocumented exclusions.
- Weighting specs without a propensity model.

Latest artifact: 240 approved specs and 5 rejected invalid fixtures.

## 7. Result

Baseline:

- PSM ATT: 1,461.2030.
- PSM 95% CI: -209.7343 to 3,132.1403.

Raw robustness surface:

- Minimum estimate: -13,104.2515.
- Median estimate: -3,146.9767.
- Maximum estimate: 2,824.8242.
- Positive estimate share: 11.7%.
- CI crosses zero share: 23.3%.

Interpretation: the paper-shaped positive matching baseline exists, but it is not stable across
the broader tested specification space.

## 8. AMD MI300X Workload

The MI300X path benchmarks batched bootstrap solves through ROCm/PyTorch:

- Same dataset hash.
- Same approved spec batch.
- CPU runtime.
- GPU runtime.
- Throughput.
- Speedup.
- CPU/GPU tolerance check.
- Hardware proof fields.

The hosted Space displays `artifacts/benchmark.json`, verifies `benchmark.json.sha256`,
and exposes `methodology/hardware.log` after the MI300X run.

## 9. Why This Matters

SpecCurve gives reviewers and methods instructors a practical way to inspect robustness without
turning the product into a truth oracle. It makes the analysis space explicit, repeatable, and
auditable.

## 10. Submission Status

Ready locally:

- Hugging Face Space files.
- Frozen NBER artifacts.
- Deterministic verifier/report flow.
- Local submission zip.
- AMD benchmark and backend code path.
- Demo script and cover asset.

External blockers:

- Run MI300X benchmark and add `artifacts/benchmark.json`,
  `artifacts/benchmark.json.sha256`, and `artifacts/methodology/hardware.log`.
- Publish Hugging Face Space.
- Provide public repository URL.
- Submit final URL and presentation assets.
