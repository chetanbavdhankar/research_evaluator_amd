# Submission Packet

## Project Name

SpecCurve L0 AMD MI300X Evidence Lab

## Short Description

SpecCurve builds a reviewer-grade specification robustness report for one public research claim.
This L0 demo uses frozen NBER LaLonde source files, verifies a pre-declared matching/weighting
specification grid, computes the robustness surface, and displays MI300X benchmark proof when
`benchmark.json` is generated on AMD ROCm hardware.

## Long Description

SpecCurve is not an independent repeat-study conclusion or final scientific adjudicator. It is a deterministic evidence workflow
for asking whether a result is stable across defensible analysis choices.

The demo starts with the NBER Dehejia-Wahba NSW treated sample plus PSID controls. It records
source file hashes, locks the claim to the ATT of NSW training on 1978 earnings, generates a
240-spec Wiki C grid, rejects invalid specs, computes the result table, renders a robustness
surface, and exports a cautious report. The AMD path benchmarks batched statistical work on
MI300X using ROCm/PyTorch and records device, throughput, speedup, and tolerance evidence.

## Links To Fill At Submission Time

| Field | Value |
| --- | --- |
| Hugging Face Space | TODO |
| Public GitHub repository | TODO |
| Demo video | `assets/demo-loop.gif` is available as a lightweight preview; final MP4 TODO |
| Slide deck | `assets/slides.html` and `docs/PITCH_DECK.md` |
| Cover image | `assets/cover.svg` and `assets/cover.png` |
| Static Space bundle | `dist/hf-static-space-export.zip` |
| Gradio companion bundle | `dist/hf-space-export.zip` |
| AMD backend URL | Optional companion endpoint: `http://165.245.141.127:8000` after backend is running |
| Build-in-public drafts | `docs/BUILD_IN_PUBLIC_DRAFTS.md` |
| AMD/ROCm feedback note | `docs/AMD_ROCM_FEEDBACK.md` |

## Tags

- AMD
- ROCm
- MI300X
- Hugging Face Space
- Gradio
- causal inference
- robustness
- reproducibility

## Final Local Commands

```bash
python -m unittest discover -s tests
python -m compileall -q app.py speccurve_l0 scripts tests
python scripts/run_pipeline.py --source nber-psid --allow-network
python scripts/export_static_space.py
python scripts/export_hf_space.py
python scripts/package_submission.py
python scripts/check_submission.py
```

Equivalent local finalization command:

```bash
python scripts/finalize_submission.py
```

## MI300X Commands

```bash
pip install -r requirements-amd.txt
python scripts/mi300x_preflight.py
python scripts/run_pipeline.py --source nber-psid --allow-network
python scripts/run_benchmark.py --require-mi300x --resamples-per-spec 256 --spec-limit 64
python scripts/import_benchmark.py artifacts/benchmark.json --hardware-log artifacts/methodology/hardware.log
python scripts/start_amd_backend.py --host 0.0.0.0 --port 8000
```

Use the ROCm-enabled PyTorch from the AMD image or official ROCm wheel index before running
these commands. The project requirements avoid installing plain `torch` so the ROCm build is
not replaced by a CPU wheel.

Equivalent bundled run:

```bash
chmod +x scripts/amd_devcloud_run.sh
RESAMPLES_PER_SPEC=256 SPEC_LIMIT=64 START_BACKEND=1 ./scripts/amd_devcloud_run.sh
```

The bundled run rebuilds the upload bundles after the benchmark so they include
`benchmark.json`, `benchmark.json.sha256`, and `methodology/hardware.log`.

## Caution Language

Use:

```text
Under this tested specification space, the result appears specification-sensitive.
```

Avoid unsupported claims that say the product settles whether the paper is right or wrong.

```text
This public-data robustness pass settles the paper.
This output alone validates the original causal claim.
This output alone invalidates the original causal claim.
```
