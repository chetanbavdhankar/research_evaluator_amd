# Opus 4.7 Recommendations For Data Sets

Detailed GPT-5.5 re-ranking of candidate datasets against the full SpecCurve wiki gates.

Metadata:

```yaml
type: review
status: advisory
generated_by: gpt-5.5
generated_at: 2026-05-06
target_folder: speccurve-wiki
decision_use: dataset_selection_support
primary_contracts:
  - speccurve-wiki/08-data-and-claim-contract.md
  - speccurve-wiki/09-gpu-and-benchmark-contract.md
  - speccurve-wiki/10-eval-gates.md
  - speccurve-wiki/11-demo-contract.md
  - speccurve-wiki/12-risk-register.md
  - speccurve-wiki/14-quality-lint.md
  - speccurve-wiki/19-product-lens-review-v3.md
```

## Executive Recommendation

Use **LaLonde NSW with PSID-1 controls** if SpecCurve is positioned primarily for
causal-inference and methods-review users.

Use **Project STAR** if the hackathon demo must be maximally legible to general judges:
education, randomized assignment, small classes, and test scores are explainable in seconds.

Use **ManyBabies 1** only if the team decides that low ethical risk and open-science fit matter
more than causal-methods relevance.

Final recommended order:

1. LaLonde NSW extended, PSID-1 controls
2. Project STAR
3. ManyBabies 1
4. Many Labs 2
5. Facial Feedback Registered Replication Report

This differs from the earlier Opus-style ranking in two important ways:

- LaLonde should not be scored as a clean 175/180 because the NBER source states
  attributable non-commercial use, and the data includes earnings, race/ethnicity, and job
  training status.
- Project STAR should be raised above ManyBabies because the AER public access data has
  stronger raw scale, richer multi-year design choices, and a more judge-legible causal story.

## Scoring Method

Scores use the weighted rubric from `08-data-and-claim-contract.md`.

| Criterion | Weight |
|---|---:|
| Baseline reproducibility | 5 |
| Clean public data/license | 5 |
| Demo legibility | 5 |
| Meaningful specification dimensions | 5 |
| GPU workload quality | 5 |
| Low ethical/legal risk | 4 |
| Time to implement | 4 |
| Reviewer relevance | 3 |

Each raw criterion is scored from 0 to 5. Maximum weighted total is 180.

The score is then interpreted through hard gates from the rest of the wiki:

- Dataset must be public, citable, licensed, locally freezeable, and tied to one narrow claim.
- Baseline must be deterministic and reproducible or approximable quickly.
- Spec space needs at least 50 early valid specs and a credible path to 200+ final specs.
- GPU work must be load-bearing: same data, same specs, same resamples, CPU/GPU tolerance pass.
- Demo must fit the two-minute story: paper, claim, baseline, specs, invalid rejection,
  MI300X batch, robustness surface, cautious conclusion.
- Public wording must avoid proof, replication verdict, truth verdict, fraud, or misconduct claims.

## Final Ranking

| Rank | Dataset | Score | Recommended claim | Primary reason |
|---:|---|---:|---|---|
| 1 | LaLonde NSW extended, PSID-1 controls | 170 | In the Dehejia-Wahba NSW + PSID-1 design, do defensible matching, weighting, and outcome-model specifications estimate a positive ATT for 1978 real earnings? | Best fit to specification-curve logic and causal-methods reviewer expectations. |
| 2 | Project STAR | 165 | The randomized small-class assignment estimated a positive effect on K-3 reading/math achievement, and SpecCurve tests how stable that estimate is across defensible analysis choices. | Best judge-legible public-policy demo with strong real spec dimensions and larger data than LaLonde. |
| 3 | ManyBabies 1 | 162 | Infants prefer infant-directed speech over adult-directed speech under defensible analysis choices. | Safest open-science candidate with low ethical risk and rich multi-lab methods variation. |
| 4 | Many Labs 2, one frozen low-risk effect | 155.5 | One selected effect from Many Labs 2 remains positive/mixed/fragile across defensible site and analysis choices. | Strongest raw GPU-scale candidate, but scope-control risk is high. |
| 5 | Facial Feedback Registered Replication Report | 152.5 | Smile vs pout condition changes cartoon funniness ratings under defensible analysis choices. | Very legible and safe, but thinner specification and GPU story. |

## 1. LaLonde NSW Extended, PSID-1 Controls

Score: **170/180**

Recommended status: **Primary if methods-reviewer credibility is the top priority.**

### Source And Data Shape

Primary sources:

- NBER/Dehejia data page: `https://users.nber.org/~rdehejia/nswdata2.html`
- Dehejia and Wahba 1999 JASA paper: `https://doi.org/10.1080/01621459.1999.10473858`
- NBER working paper: `https://www.nber.org/papers/w6586`
- `lmw` R documentation: `https://search.r-project.org/CRAN/refmans/lmw/html/lalonde.html`
- `kbal` R documentation: `https://rdrr.io/cran/kbal/man/lalonde.html`

The extended PSID-1 version contains 185 NSW treated units and 2,490 PSID controls,
for 2,675 rows. Core variables include treatment, age, education, race/ethnicity,
marital status, no-degree indicator, real earnings in 1974, real earnings in 1975,
and real earnings in 1978.

### Claim

Use this wording:

> In the Dehejia-Wahba NSW + PSID-1 design, do defensible matching, weighting, and
> outcome-model specifications estimate a positive average treatment effect on 1978
> real earnings, and how stable is that estimate?

Avoid this wording:

> NSW job training raised 1978 real earnings vs. PSID-1 control sample.

Reason: PSID-1 is a nonexperimental comparison group. Strong causal wording would
violate the wiki's anti-overclaiming rules unless the report carefully distinguishes
experimental benchmark, observational comparison, and specification robustness.

### Specification Dimensions

This is the strongest candidate for meaningful specification variation.

Defensible dimensions:

- Matching or weighting method: propensity-score matching, IPW, overlap weighting,
  Mahalanobis matching, coarsened exact matching.
- Propensity model: logit, probit, flexible tree/GBM model if implementation time allows.
- Covariate set: demographics only, demographics plus prior earnings, prior earnings plus
  unemployment proxies, interactions.
- Support rule: no trimming, common-support trimming, caliper thresholds, weight clipping.
- Outcome scale: raw `re78`, log1p `re78`, zero-earnings indicator as sensitivity.
- Outcome model: difference in means after preprocessing, linear regression adjustment,
  doubly robust estimator.
- Estimand guardrail: ATT only for the primary demo; reject ATE/ATC drift unless explicitly
  configured.

This easily supports 200+ defensible specifications without artificial variation.

### GPU Workload

The honest MI300X workload is:

```text
approved specs x bootstrap resamples x effect estimators
```

Each bootstrap replicate should refit the matching/weighting path for that spec, not merely
resample a final effect table. That makes the GPU batch product-linked: the robustness surface
depends on the GPU-generated result table.

The caveat is small raw N. The demo must say:

> The GPU advantage comes from parallel `specification x bootstrap` evaluation, not from a
> large row count.

### Main Risks

- Data use is attributable non-commercial on the NBER page, not unrestricted CC0.
- Sensitive variables include earnings, race/ethnicity, and unemployment/job-training status.
- Causal wording can drift into overclaiming.
- Some matching algorithms may be CPU-oriented unless rewritten or simplified for the first
  MI300X proof.

### Hard-To-Vary Verdict

LaLonde wins because the product mechanism and dataset mechanism are the same. SpecCurve
exists to show how defensible analysis choices move a claim. The LaLonde benchmark exists
because causal estimates change under observational design and adjustment choices. Replacing
LaLonde as rank #1 requires a candidate with equally canonical methods relevance, cleaner
license, and stronger GPU workload. The current pool does not have that combination.

## 2. Project STAR

Score: **165/180**

Recommended status: **Primary if judge-legibility and public-policy demo value are the top priority.**

### Source And Data Shape

Primary sources:

- AER `STAR` documentation: `https://search.r-project.org/CRAN/refmans/AER/html/STAR.html`
- Krueger NBER paper: `https://www.nber.org/papers/w6051`
- QJE article page: `https://academic.oup.com/qje/article/114/2/497/1844226`

The AER `STAR` data is documented as 11,598 observations and 47 variables. It includes
class type by grade, math and reading scaled scores by grade, lunch status, school type,
school/system IDs, teacher characteristics, and student demographics.

### Claim

Use this wording:

> The randomized small-class assignment estimated a positive effect on K-3 reading/math
> achievement, and SpecCurve tests how stable that estimate is across defensible choices
> about grade, outcome, attrition, school structure, and covariate adjustment.

Short demo wording:

> Did small K-3 classes improve reading and math scores, and does that conclusion survive
> reasonable analysis choices?

### Specification Dimensions

Project STAR has more real dimensions than the earlier ranking gave it credit for.

Defensible dimensions:

- Outcome: reading, math, sum, z-scored composite.
- Grade scope: kindergarten only, grade 1, grade 2, grade 3, pooled K-3.
- Treatment definition: assigned small class, attended small class, years in small class.
- Model structure: simple OLS, school fixed effects, grade fixed effects, school-by-grade
  fixed effects, hierarchical/multilevel model.
- Attrition handling: complete case, late entrants excluded, late entrants included,
  inverse-probability attrition weights if time allows.
- Covariates: none, demographics, free-lunch status, teacher experience, school type.
- Uncertainty: robust SE, school-clustered SE, clustered bootstrap.

This supports 200+ specs without padding.

### GPU Workload

The honest MI300X workload is:

```text
approved specs x clustered bootstrap resamples x grade/outcome/model variants
```

The first GPU proof should focus on fixed-effect or matrix-based estimators plus clustered
bootstrap. HLM/multilevel refits should not be claimed as GPU-backed unless implemented in
a numerically equivalent GPU path.

### Main Risks

- Multi-year reshaping and validation can consume about one build day.
- Exact Krueger replication may require careful handling of percentiles, attrition, and
  class transitions.
- Student data and race/free-lunch variables require careful public wording, though the
  policy context is lower risk than misconduct or medical claims.
- If the team implements HLM first, the AMD proof may become slower or CPU-bound.

### Hard-To-Vary Verdict

Project STAR ranks above ManyBabies because it gives judges a clearer reason to care:
small classes, children, test scores, and education spending. It also gives reviewers a real
robustness problem: attrition, class transitions, school structure, outcome choice, and
clustering. It ranks below LaLonde only because LaLonde is more directly recognized as a
methods benchmark and is faster to baseline.

## 3. ManyBabies 1

Score: **162/180**

Recommended status: **Best low-risk open-science fallback.**

### Source And Data Shape

Primary sources:

- Paper: `https://journals.sagepub.com/doi/10.1177/2515245919900809`
- OSF project: `https://osf.io/re95x/`
- GitHub analysis repository: `https://github.com/manybabies/mb1-analysis-public`

The paper reports open data, open materials, and preregistration. The GitHub repository
contains data and code and is MIT licensed.

### Claim

> Infants prefer infant-directed speech over adult-directed speech under defensible analysis
> choices.

### Specification Dimensions

- Lab inclusion.
- Age band.
- Native language/background.
- Looking-time aggregation.
- Exclusion rules.
- Trial filtering.
- Model family.
- Random effects or lab adjustment.
- Bootstrap/permutation uncertainty.

### GPU Workload

Batched bootstrap across labs and approved specs is honest, though the workload is less
obviously tied to causal-methods review than LaLonde or STAR.

### Main Risks

- Mixed-effects modeling can add implementation complexity.
- The claim is scientifically clean but less instantly connected to policy or methods review.
- Some judges may find the domain less consequential than education or job training.

### Hard-To-Vary Verdict

ManyBabies is the safest scientifically and ethically. It loses to LaLonde and STAR because
SpecCurve's target user is a reviewer/methods instructor inspecting analysis-dependence, and
causal/policy examples make that value easier to see.

## 4. Many Labs 2

Score: **155.5/180**

Recommended status: **Use only if raw GPU scale is the overriding priority.**

### Source And Data Shape

Primary sources:

- Paper: `https://journals.sagepub.com/doi/10.1177/2515245918810225`
- OSF project: `https://osf.io/8cd4r/`
- GitHub repository: `https://github.com/ManyLabsOpenScience/ManyLabs2`
- Dataset record: `https://pure.hud.ac.uk/en/datasets/many-labs-2-investigating-variation-in-replicability-across-sampl/`

Many Labs 2 includes 28 findings, 125 samples, and 15,305 participants. The dataset record
lists OSF publication and CC0 1.0 Universal license.

### Claim

The claim must be frozen to one effect. Do not build a demo around all 28 findings.

Safer wording:

> For one selected Many Labs 2 effect, SpecCurve tests whether the estimated effect remains
> positive, mixed, fragile, or inconclusive across defensible site and analysis choices.

### Specification Dimensions

- Site inclusion.
- Language/country grouping.
- Attention or quality exclusions.
- Demographic covariates.
- Fixed-effect vs multilevel site handling.
- Outcome transformation.
- Weighting and resampling choices.

### GPU Workload

This is the strongest raw batch candidate: `125 sites x specs x bootstrap` is naturally
parallel. The AMD story is strong if the selected effect has a clean outcome and simple
effect estimator.

### Main Risks

- Choosing among 28 effects creates scope drift.
- Demo can become a replication-crisis lecture.
- Some effects may carry awkward or sensitive interpretation.
- Data/code structure may take time to navigate.

### Hard-To-Vary Verdict

Many Labs 2 is technically powerful but product-risky. It should not beat LaLonde or STAR
unless the submission strategy prioritizes MI300X throughput above two-minute comprehension.

## 5. Facial Feedback Registered Replication Report

Score: **152.5/180**

Recommended status: **Clean fallback if implementation time collapses.**

### Source And Data Shape

Primary sources:

- Paper DOI: `https://doi.org/10.1177/1745691616674458`
- OSF project: `https://osf.io/pkd65/`

The study is a registered replication report of Strack, Martin, and Stepper's facial-feedback
effect, using multiple labs and a simple smile/pout funniness-rating design.

### Claim

> Smile vs pout condition changes cartoon funniness ratings under defensible analysis choices.

### Specification Dimensions

- Lab inclusion.
- Exclusion rules.
- Awareness/guessing exclusions.
- Outcome aggregation.
- Fixed vs random lab handling.
- Robust vs classical uncertainty.
- Bootstrap/permutation settings.

### GPU Workload

GPU use is possible through batched bootstrap, but weaker than LaLonde, STAR, or Many Labs 2
because the core estimator is simple and the spec space is narrower.

### Main Risks

- GPU workload can look synthetic.
- The result may be too flat for a compelling robustness surface.
- It is easy to slide into "replication failed" language, which the wiki bans.

### Hard-To-Vary Verdict

Facial Feedback is excellent for clarity and low risk, but it is not the best final dataset
for an AMD hackathon. It should remain a fallback, not the primary.

## Explicitly Not Recommended As Final Dataset

### Many Analysts, One Data Set

Technical fit is very high, but final-demo risk is too high.

Reason:

- The topic involves race/skin-tone and referee punishment decisions.
- The demo could be interpreted as making a discrimination verdict.
- This conflicts with the wiki's anti-overclaiming and low-risk demo constraints.

Use only as a private technical benchmark or future example.

### Berkeley Admissions

Useful as a teaching mock, not as the final AMD proof.

Reason:

- Too small.
- Too familiar.
- Weak GPU workload.
- Already superseded by the wiki decision logic as a final dataset.

### Reproducibility Project: Psychology Aggregate Data

Not recommended for MVP.

Reason:

- Violates the "one paper, one dataset, one claim" constraint.
- Produces a meta-level demo rather than a reviewer-grade robustness report for one claim.

## Final Recommendation For The Decision Record

Fill `speccurve-wiki/decisions/0001-final-dataset-and-claim.md` with:

```yaml
selected_dataset: LaLonde NSW extended with PSID-1 controls
fallback_dataset: Project STAR
selected_claim: >
  In the Dehejia-Wahba NSW + PSID-1 design, do defensible matching,
  weighting, and outcome-model specifications estimate a positive ATT for
  1978 real earnings, and how stable is that estimate?
fallback_claim: >
  The randomized small-class assignment estimated a positive effect on K-3
  reading/math achievement, and SpecCurve tests how stable that estimate is
  across defensible analysis choices.
primary_reason: >
  LaLonde best matches SpecCurve's mechanism: causal estimates move under
  defensible preprocessing, matching, weighting, trimming, and outcome-model
  choices.
risk_note: >
  Use cautious language because the PSID comparison is nonexperimental and the
  data use is attributable non-commercial.
```

If implementation time is the dominant constraint after the first baseline attempt, switch to
Project STAR. If risk and open-science optics become the dominant constraint, switch to
ManyBabies 1.

## Verification Still Required Before Final Lock

This file is an advisory ranking. It does not close the Dataset gate by itself.

Before claiming final selection:

1. Download or load the selected data from the cited source.
2. Freeze local raw files and record hashes.
3. Record license and citation in `data/metadata.json`.
4. Reproduce or approximate the baseline result.
5. Generate at least 50 valid early specifications.
6. Prove a path to 200+ final specifications.
7. Run one CPU/GPU batched-bootstrap prototype with matching tolerance.

