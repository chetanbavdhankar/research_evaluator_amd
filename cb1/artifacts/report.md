# SpecCurve L0 Evidence Report

## Claim Under Test

In a LaLonde-style NSW job-training design, do defensible matching, weighting, and outcome-model specifications estimate a positive ATT for 1978 real earnings, and how stable is that estimate?

## Dataset Card

- Dataset id: `nber-dehejia-wahba-nsw-treated-psid1-controls`
- Dataset hash: `a3a1ae1a7d599650b2a48f3c203764dd04803a994bcb6899e9ccf246168c4081`
- Row count: 2675
- Source: NBER Dehejia-Wahba NSW treated sample plus PSID controls
- Evidence status: frozen_nber_source_psid1_controls

## Warnings

- NBER states these data are distributed for attributable non-commercial use.
- Cite Dehejia and Wahba 1999, Dehejia and Wahba 2002, and LaLonde 1986.
- Raw source files frozen in artifacts/data/raw-nber-psid with SHA-256 hashes.

## Frozen Source Files

- `nswre74_treated.txt` from https://www.nber.org/~rdehejia/data/nswre74_treated.txt (sha256 `e7b742fe0ff07a0f45e129b4ff108bb9611cd83d53604732c48a8a0a3e20eda3`)
- `psid_controls.txt` from https://www.nber.org/~rdehejia/data/psid_controls.txt (sha256 `73ffcdd8feb7f965f8e1de9bfdb80a095542c7a95ce7f56b2e2b2a9716e858cc`)

## Verifier Gate

- Approved specifications: 240
- Rejected invalid fixtures: 5
- Locked outcome: `re78`
- Locked treatment: `treat`

## Baseline

- Baseline id: `lalonde-att-baseline-v2`
- Unadjusted ATT: -15204.7775
- Adjusted ATT: 4.1579
- Adjusted 95% CI: -1983.2350 to 1991.5509
- PSM ATT: 1461.2030
- PSM 95% CI: -209.7343 to 3132.1403
- PSM matched treated rows: 162
- Treated/control rows: 185 / 2490

## Robustness Surface

- Approved result count: 240
- Headline surface count: 120
- Headline transform: `raw`
- Minimum estimate: -13104.2515
- Median estimate: -3146.9767
- Maximum estimate: 2824.8242
- Positive estimate share: 11.7%
- CI crosses zero share: 23.3%
- Estimator levels: `cem_att`, `ipw_att`, `mahalanobis_1nn`, `ols`, `psm_1nn`, `ridge_1e-6`
- Propensity model levels: `logit_l2`, `none`, `probit_gradient`
- Support rule levels: `caliper_0.05`, `clip_0.02_0.98`, `common_support_pscore`, `none`, `trim_0.05_0.95`
- Scale note: Headline surface statistics use raw re78 specifications only.

## AMD MI300X Benchmark

- Status: no final `benchmark.json` loaded.
- Required next run: execute `python scripts/run_benchmark.py --require-mi300x` on an AMD MI300X ROCm machine and copy the generated artifact into `artifacts/benchmark.json`.


## Interpretation Boundary

This run uses frozen NBER LaLonde source files with local hashes. The empirical interpretation is now tied to those files, but final AMD submission still requires `benchmark.json` generated on AMD MI300X/ROCm and displayed in the AMD Proof panel.
