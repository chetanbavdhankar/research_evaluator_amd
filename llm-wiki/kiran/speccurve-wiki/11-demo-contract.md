# Demo Contract

The demo must show a complete product story in two minutes. Anything that does not support this sequence is secondary.

## Two-Minute Sequence

| Time | Beat | What to show | Safe narration |
|---:|---|---|---|
| 0:00-0:10 | Paper/claim | Paper and dataset card. | "SpecCurve starts with one public paper, one public dataset, and one narrow claim." |
| 0:10-0:25 | Baseline | Baseline result and marker. | "First we reproduce or document the baseline result before generating variants." |
| 0:25-0:45 | Specs generated | Spec count and one spec detail. | "The system builds defensible analysis specifications: covariates, exclusions, transforms, models, and resampling choices." |
| 0:45-1:05 | Invalid spec rejected | Verifier panel with bad spec. | "The verifier rejects invalid plans before they touch the statistics engine." |
| 1:05-1:30 | AMD MI300X batch execution | AMD proof panel, device, batch, speedup. | "Approved specs run as a batch workload on AMD MI300X through ROCm/PyTorch." |
| 1:30-1:50 | Robustness surface | Effect/significance surface with baseline. | "The output is not one p-value. It is a map of how the result moves across defensible choices." |
| 1:50-2:00 | Cautious conclusion | Explanation panel or report preview. | "Under this tested specification space, the result is [robust/fragile/mixed/inconclusive]. This is not replication and not a truth verdict." |

## Required Demo Beats

- Paper/claim.
- Baseline.
- Specs generated.
- Invalid spec rejected.
- AMD MI300X batch execution.
- Robustness surface.
- Cautious conclusion.

## Q&A Safe Answers

| Question | Safe answer |
|---|---|
| Is this replication? | No. Replication requires independent data. SpecCurve performs specification robustness analysis on existing public data. |
| Are you proving the paper wrong? | No. We show whether the target result is stable, fragile, mixed, or inconclusive under a defined specification space. |
| What do agents actually do? | They propose structured specs, help verify them against rules, and explain computed results. Deterministic code computes statistics. |
| Why AMD MI300X? | The workload is many related statistical jobs over the same data: batched regressions, bootstraps, permutation tests, and specification sweeps. MI300X makes the surface interactive when the benchmark passes. |
| What is original? | The product combines agent-generated specs, verifier safeguards, GPU-scale execution, provenance, and an interactive robustness surface. |
| What if the GPU run is cached? | Cached runs are labeled. The demo must distinguish precomputed robustness output from live MI300X benchmark evidence. |
| Why not support arbitrary uploads? | The hackathon MVP optimizes for one defensible reviewer-grade report. Arbitrary uploads come after the baseline, verifier, and benchmark are trustworthy. |
| Who uses this first? | A statistically literate reviewer or methods instructor who wants a reproducible robustness appendix for a public result. |

## Demo Kill Conditions

- The script cannot finish in two minutes.
- The verifier rejection is not visible.
- The AMD proof panel lacks real logs.
- The robustness surface needs a private explanation to understand.
- The conclusion says or implies replication, proof, fraud, or scientific truth.
