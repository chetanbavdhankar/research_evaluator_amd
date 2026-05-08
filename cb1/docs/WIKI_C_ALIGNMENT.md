# Wiki C Alignment Notes

## Implemented In This Local Build

- L0 deterministic spine before agentic explanation.
- Frozen NBER Dehejia-Wahba NSW treated plus PSID-1 controls dataset card and hash artifact.
- Baseline/spec-grid execution across 240 approved specifications, with a path to the full
  768-spec deterministic grid.
- Matching and weighting dimensions called for by Wiki C: propensity-score matching, IPW,
  Mahalanobis matching, coarsened exact matching, logit/probit propensity models, support
  rules, covariate sets, filters, and raw/log outcome scales.
- Verifier rejects invalid specs before execution.
- Report is generated from artifacts, not from free-form agent claims.
- AMD benchmark contract is implemented as a ROCm/PyTorch artifact path with the Wiki C
  `tolerance_check: "pass|fail"` shape, `benchmark.json.sha256` sidecar, and
  `methodology/hardware.log` evidence log.
- Hugging Face Space packaging includes a strict static export under
  `dist/hf-static-space-export/` using `space/README.md`, `space/index.html`, and
  same-origin `data/*.json` artifacts.
- The static Space uses browser `SubtleCrypto` to verify `data/benchmark.json` against
  `data/benchmark.json.sha256` before showing the benchmark as ready.
- The static Space packages `methodology/hardware.log` with the benchmark so judges can
  inspect the MI300X/ROCm hardware evidence behind the displayed speedup.
- The Gradio app remains as an interactive local/companion surface, not the strict
  execution-isolated public Space path.

## Still Open For Final Submission

- The wiki decision template remains a template; the local build has operationally selected
  the NBER NSW treated plus PSID controls source and records that choice in artifacts.
- MI300X hardware cannot be truthfully claimed until `artifacts/benchmark.json`,
  `artifacts/benchmark.json.sha256`, and `artifacts/methodology/hardware.log` are generated
  on AMD MI300X.
- A human-facing validation pass remains outside this local software build.

## Guideline

Start coding from this local folder. Treat the empirical software path as Wiki C L0-ready,
with the final public submission still blocked by MI300X benchmark evidence, hosted Space
publication, public repository URL, and presentation assets.
