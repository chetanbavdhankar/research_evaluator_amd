# Build-In-Public Drafts

These are safe public drafts for the LabLab/AMD build-in-public surface. Add final Space,
repo, and benchmark links before posting.

## Update 1 - Product Design

Working title:

```text
Why one estimate is not enough: the SpecCurve L0 design
```

Draft:

```text
SpecCurve L0 is an AMD hackathon project for reviewer-grade specification robustness.

The first demo uses one public research design: the NBER Dehejia-Wahba NSW treated sample
with PSID controls. The app freezes the source files, records SHA-256 hashes, locks the
target ATT question, generates a pre-declared matching/weighting grid, and rejects invalid
analysis specs before any result is computed.

The goal is not to settle a paper. The goal is to show whether a result is stable across
defensible analysis choices that a methods reviewer would naturally inspect.

What is built now:
- Frozen dataset card
- 240 approved specs
- 5 rejected invalid fixtures
- Robustness surface
- Static Hugging Face Space export
- AMD MI300X benchmark path

Space: [add link]
Repo: [add link]

@lablab @AIatAMD
```

Suggested visual:

- `assets/cover.png`
- Static Space screenshot after upload

## Update 2 - AMD Technical Proof

Working title:

```text
MI300X benchmark: batched bootstrap for a robustness surface
```

Draft before final benchmark:

```text
SpecCurve L0 separates the public Space from the AMD compute path.

The Hugging Face Space is static: it renders precomputed JSON/SVG artifacts and verifies
the benchmark SHA-256 in the browser. The numerical workload runs on AMD Developer Cloud:
same dataset, same approved spec batch, same resampling count, CPU/GPU tolerance check,
hardware metadata written into benchmark.json, and a separate hardware log.

Current benchmark status: pending final MI300X run.

Planned command:
python scripts/run_benchmark.py --require-mi300x --resamples-per-spec 256 --spec-limit 64

Space: [add link]
Repo: [add link]

@lablab @AIatAMD
```

Draft after benchmark:

```text
SpecCurve L0 now has the AMD proof artifact.

The benchmark runs the same batched bootstrap workload on CPU and AMD MI300X through
ROCm/PyTorch, compares numerical outputs within tolerance, and writes hardware, HIP,
runtime, throughput, speedup, SHA-256 evidence, and hardware log evidence into the
benchmark bundle.

Benchmark:
- GPU: [add GPU name]
- HIP/ROCm: [add version]
- Specs x resamples: [add count]
- Speedup: [add measured value only]
- Tolerance: [pass/fail]

The public Hugging Face Space is still static. It displays the artifact and verifies the
benchmark hash client-side.

Space: [add link]
Repo: [add link]

@lablab @AIatAMD
```

Suggested visual:

- AMD Proof tab from the static Space after `benchmark.json` is packaged.
- `artifacts/benchmark.json` snippet showing hardware and tolerance.
- `artifacts/methodology/hardware.log` snippet showing the MI300X/ROCm capture.

## Posting Checklist

- Run `python scripts/finalize_submission.py` first.
- Add Space and repo links.
- Add measured benchmark values only after `submission_ready` is true.
- Do not claim speedup before the benchmark artifact exists.
- Keep the wording to robustness evidence, not final scientific adjudication.
