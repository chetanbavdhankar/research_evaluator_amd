# AMD Developer Cloud And ROCm Feedback

This note is prepared for the LabLab/AMD feedback surface. Fill the bracketed fields after
the final MI300X run.

## Context

We used AMD Developer Cloud and ROCm/PyTorch to run the SpecCurve L0 numerical benchmark:
batched bootstrap solves over approved Wiki C LaLonde outcome-model specifications.

The public Hugging Face Space is intentionally static. AMD Developer Cloud is where the
dataset pipeline, benchmark, and optional backend run.

## What Worked

- The MI300X target is easy to make evidence-backed when the benchmark logs GPU name,
  HIP/ROCm version, PyTorch version, CPU runtime, GPU runtime, tolerance status, and a
  separate hardware evidence log.
- Separating the static Space from the AMD compute host creates a clean security boundary:
  the public app displays artifacts, while ROCm/PyTorch does numerical work on the cloud VM.
- The large-memory GPU path fits the product shape: many related statistical jobs over the
  same frozen dataset and spec batch.

## What Was Confusing Or Slow

- The Space-vs-cloud workflow needs explicit documentation. A new builder may assume the
  public Space should run the GPU workload, while this project needs a static public viewer
  plus an AMD-generated benchmark artifact.
- Dependency setup depends on matching PyTorch, HIP, and ROCm builds. A known-good AMD
  Developer Cloud template for PyTorch benchmarking would reduce setup time.
- Network and firewall behavior for exposing an optional backend should be surfaced clearly
  in the DevCloud UI, especially when teams want a read-only health endpoint.

## What Would Improve The Developer Experience

- Provide a compact ROCm/PyTorch benchmark starter that logs:
  `gpu`, `hip`, `torch`, CPU runtime, GPU runtime, speedup, tolerance, warmup policy, and
  a raw hardware log.
- Provide a recommended pattern for Hugging Face static Space plus AMD Developer Cloud
  artifact generation.
- Add a short guide for safely exposing a read-only health endpoint from DevCloud when a
  Space wants to display live hardware status.

## Evidence To Fill

```text
Benchmark artifact: [link to benchmark.json]
Benchmark SHA-256: [link to benchmark.json.sha256]
Hardware log: [link to methodology/hardware.log or pasted hardware block]
Space: [link]
Repo: [link]
GPU: [AMD Instinct MI300X string]
HIP/ROCm: [version]
PyTorch: [version]
Speedup: [measured value only]
Tolerance: [pass/fail]
```
