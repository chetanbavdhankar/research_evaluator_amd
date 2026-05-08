---
title: SpecCurve L0 AMD MI300X Evidence Lab
sdk: gradio
python_version: "3.11"
app_file: app.py
tags:
  - amd
  - rocm
  - mi300x
  - reproducibility
  - causal-inference
---

# SpecCurve L0 AMD MI300X Evidence Lab

This folder is a separate local build based on the Wiki C blueprint. It packages a Hugging Face Space webapp and a deterministic evidence pipeline for the AMD hackathon.

## What Is Built

- Dataset card and hash artifact.
- Locked LaLonde-style claim surface.
- Pre-declared 240-spec Wiki C grid spanning OLS, ridge, propensity-score matching,
  IPW, Mahalanobis matching, and coarsened exact matching.
- Verifier that rejects claim mutation, outcome leakage, missing columns, and undocumented exclusions.
- Result table and robustness surface.
- Markdown report artifact.
- ROCm/PyTorch benchmark path that emits the required MI300X `benchmark.json`,
  `benchmark.json.sha256`, and `methodology/hardware.log` evidence bundle.
- Gradio webapp for hosted review on Hugging Face Spaces.
- Static Hugging Face Space export for the strict Wiki C execution-isolation path.

## Local Core Run

```bash
python scripts/run_pipeline.py --source demo
```

The default demo source is synthetic and only validates the software spine. It is not empirical claim evidence.

To run the public fallback dataset adapter:

```bash
python scripts/run_pipeline.py --source rdatasets --allow-network
```

That fallback is still not the final Wiki C extended PSID decision. The final gate needs frozen source files, license/citation evidence, and hashes.

To run the frozen NBER Dehejia-Wahba NSW treated plus PSID controls source:

```bash
python scripts/run_pipeline.py --source nber-psid --allow-network
```

This freezes the raw NBER text files under `artifacts/data/raw-nber-psid`, records their
SHA-256 hashes, derives `u74` and `u75` unemployment indicators, and regenerates the
visible report from the 240-spec matching/weighting/outcome-model grid.

## AMD MI300X Benchmark Run

Run this on an AMD MI300X ROCm host after the pipeline has produced artifacts:

```bash
pip install -r requirements-amd.txt
python scripts/mi300x_preflight.py
python scripts/run_benchmark.py --require-mi300x --resamples-per-spec 256 --spec-limit 64
```

`requirements-amd.txt` intentionally does not install `torch`. Use the ROCm-enabled PyTorch
that comes with the AMD image, or install PyTorch from the official ROCm-specific wheel
index for that host. The preflight fails if PyTorch is CPU-only or if `torch.version.hip`
is missing.

The app treats `artifacts/benchmark.json` plus `artifacts/methodology/hardware.log` as
the hardware proof. Hugging Face provides the hosted webapp surface; the MI300X proof
comes from the ROCm benchmark artifact.
The benchmark run also writes `artifacts/benchmark.json.sha256` and re-renders
`artifacts/report.md` so the exported Space has both the visible benchmark block and the
hash sidecar for the Wiki C AMD gate.

If the benchmark is generated on a separate AMD checkout, import it into this local folder with:

```bash
python scripts/import_benchmark.py path/to/benchmark.json --hardware-log path/to/hardware.log
```

That command validates the Wiki C benchmark contract, requires the accompanying hardware
log, writes the SHA-256 sidecar, and re-renders `artifacts/report.md` with the benchmark
block.

To expose live backend status to the Space from the current AMD Developer Cloud instance:

```bash
python scripts/start_amd_backend.py --host 0.0.0.0 --port 8000
```

Set this Space variable:

```text
AMD_BACKEND_URL=http://165.245.141.127:8000
```

## Hugging Face Space

For strict Wiki C submission, use the static Space bundle:

```bash
python scripts/export_static_space.py
```

Upload `dist/hf-static-space-export/` or `dist/hf-static-space-export.zip` to a Hugging
Face Space with `sdk: static`. This public Space renders precomputed artifacts only: no
server-side execution, no uploads, no user-supplied code, and no backend dependency.

The Gradio app remains available as an interactive local/companion Space path. To build that
bundle:

```bash
python scripts/export_hf_space.py
```

The Space should include the final `artifacts/benchmark.json`, `artifacts/benchmark.json.sha256`,
and `artifacts/methodology/hardware.log` generated on AMD MI300X before submission. Do not
claim MI300X acceleration from the Space runtime unless it is actually running on MI300X/ROCm.

## Submission Assets

- Cover image: `assets/cover.png` and `assets/cover.svg`.
- Animated preview: `assets/demo-loop.gif`.
- HTML slide deck: `assets/slides.html`.
- Demo script: `docs/DEMO_SCRIPT.md`.
- Pitch outline: `docs/PITCH_DECK.md`.
- Submission copy packet: `docs/SUBMISSION_PACKET.md`.
- Completion audit: `docs/COMPLETION_AUDIT.md`.

Regenerate local image assets with:

```bash
python scripts/create_submission_assets.py
```

Refresh the uploadable local zip with:

```bash
python scripts/package_submission.py
python scripts/write_package_checksums.py
```

Build a Hugging Face Space upload folder and zip with:

```bash
python scripts/export_hf_space.py
python scripts/export_static_space.py
```

Run the local readiness gate with:

```bash
python scripts/check_submission.py
```

Run the full local finalization loop with:

```bash
python scripts/finalize_submission.py
```

The in-app demo button writes to `artifacts-demo/` by default. It does not overwrite the
frozen NBER evidence artifacts in `artifacts/`.
