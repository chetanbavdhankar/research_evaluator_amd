# Two-Minute Demo Script

## Setup

- Open the Hugging Face Space or local app.
- Use the already-generated NBER artifacts.
- Keep the AMD Proof tab ready to show `benchmark.json`, `benchmark.json.sha256`, and
  `methodology/hardware.log` after the MI300X run.

## Script

| Time | Screen | Narration |
| ---: | --- | --- |
| 0:00 | Report tab, dataset card | "SpecCurve starts with one public paper-style dataset, one narrow claim, and frozen source files. Here the data are the NBER Dehejia-Wahba NSW treated sample plus PSID controls." |
| 0:15 | Frozen source files | "The raw source files are frozen locally and hashed, so the report is tied to exact bytes rather than a moving spreadsheet." |
| 0:30 | Baseline section | "First we show the baseline. The paper-shaped propensity-score matching baseline is positive, but the interval crosses zero." |
| 0:45 | Verifier gate | "Before any statistics run, the verifier locks the outcome, treatment, and allowed spec dimensions. It rejects claim changes, leakage, missing columns, undocumented exclusions, and invalid weighting specs." |
| 1:05 | Surface tab | "The system then computes 240 defensible specs across OLS, ridge, propensity-score matching, IPW, Mahalanobis matching, CEM, filters, support rules, and outcome scales." |
| 1:25 | Surface result table | "The result is a surface, not a single p-value. In this tested raw-scale surface, only 11.7 percent of estimates are positive." |
| 1:40 | AMD Proof tab | "The AMD path runs a batched bootstrap benchmark on MI300X through ROCm/PyTorch and records hardware, speedup, throughput, CPU/GPU tolerance, SHA-256, and the hardware log as AMD gate evidence." |
| 1:55 | Report conclusion | "The cautious conclusion is specification sensitivity: the paper-like matching baseline exists, but it is not stable across this tested specification space. This is not an independent repeat-study conclusion or final scientific adjudication." |

## Safe Q&A

| Question | Answer |
| --- | --- |
| Is this replication? | No. Replication needs independent data. This is specification robustness on public source files. |
| Are you saying the paper is wrong? | No. The product shows how the estimate moves under a defined, defensible spec space. |
| Why MI300X? | The workload is many related statistical jobs over the same data: specification sweeps and bootstrap batches. |
| What is deterministic? | Dataset freezing, spec generation, verifier gates, statistical computation, report rendering, and benchmark artifact schema. |
| What is agentic? | Agents can propose and explain structured specs, but deterministic code verifies specs and computes statistics. |
