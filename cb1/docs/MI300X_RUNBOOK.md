# AMD MI300X Benchmark Runbook

## Purpose

The benchmark documents that the numerical robustness workload runs on AMD MI300X through
ROCm/PyTorch. The hosted static Hugging Face Space displays this proof, but the benchmark
artifact must be generated on AMD hardware.

The current L0 benchmark kernel times batched bootstrap solves for the approved linear
outcome-model subset of the Wiki C grid. Matching/weighting estimators are included in the
main robustness report and are listed as excluded estimator levels in `benchmark.json`.

## Prerequisites

- AMD MI300X machine with ROCm-enabled PyTorch.
- Pipeline artifacts already created in `artifacts/`.
- Final frozen dataset source and hashes recorded before public submission.

`requirements-amd.txt` intentionally does not install `torch`. Use the ROCm-enabled PyTorch
provided by the AMD image, or install PyTorch from the official ROCm-specific wheel index for
that host before running this project. A plain PyPI `torch` install can replace the ROCm build
with a CPU build, so `scripts/mi300x_preflight.py` checks `torch.cuda.is_available()`,
`torch.version.hip`, the MI300X device name, and a GPU tensor smoke test before the benchmark.

## Commands

```bash
pip install -r requirements-amd.txt
python scripts/mi300x_preflight.py
python scripts/run_pipeline.py --source csv --csv-path path/to/frozen_lalonde.csv
python scripts/run_benchmark.py --require-mi300x --resamples-per-spec 256 --spec-limit 64
python scripts/start_amd_backend.py --host 0.0.0.0 --port 8000
```

For the NBER Dehejia-Wahba NSW treated plus PSID controls source:

```bash
python scripts/run_pipeline.py --source nber-psid --allow-network
python scripts/mi300x_preflight.py
python scripts/run_benchmark.py --require-mi300x --resamples-per-spec 256 --spec-limit 64
python scripts/start_amd_backend.py --host 0.0.0.0 --port 8000
```

Or run the bundled DevCloud handoff script:

```bash
chmod +x scripts/amd_devcloud_run.sh
RESAMPLES_PER_SPEC=256 SPEC_LIMIT=64 START_BACKEND=1 ./scripts/amd_devcloud_run.sh
```

For a benchmark-only run that does not start the backend:

```bash
START_BACKEND=0 ./scripts/amd_devcloud_run.sh
```

The handoff script runs `scripts/mi300x_preflight.py`, the pipeline, benchmark, local tests,
asset refresh, Hugging Face export, submission zip packaging, and readiness checker in
sequence. When it finishes, the fresh static and Gradio export zips include the MI300X
benchmark artifacts.

The preflight must report `preflight_status=pass`. A pass means PyTorch is importable,
`torch.version.hip` is populated, PyTorch sees an MI300-class GPU, and a small tensor smoke
test runs on `cuda`.

For a software-only rehearsal:

```bash
python scripts/run_pipeline.py --source demo
```

Do not use the demo fixture for empirical claims.

## Required Artifact

The MI300X run writes:

```text
artifacts/benchmark.json
artifacts/benchmark.json.sha256
artifacts/methodology/hardware.log
```

The artifact contains:

- Dataset hash.
- Spec batch id.
- Approved spec count.
- Benchmark scope and excluded estimator levels.
- Resamples per spec.
- CPU and GPU runtime.
- Speedup and throughput.
- Tolerance comparison.
- Hardware fields for CPU, GPU, ROCm, Torch, and HIP.
- `submission_ready` boolean.

`artifacts/methodology/hardware.log` records the benchmark id, dataset hash, spec batch id,
benchmark file SHA-256, benchmark hardware JSON, detected hardware JSON, runtime summary,
and best-effort `rocm-smi` output. It is required by the Wiki C AMD gate evidence bundle.

`scripts/run_benchmark.py` also re-renders `artifacts/report.md` so the hosted Space
can show the benchmark block after the artifact is produced.

If the benchmark was generated in another checkout, copy it and the matching hardware log
into this folder through the validated import command:

```bash
python scripts/import_benchmark.py path/to/benchmark.json --hardware-log path/to/hardware.log
```

The import command checks the dataset hash, MI300X hardware string, HIP field, tolerance
status, speedup formula, total run formula, `submission_ready`, and the Wiki C
`tolerance_check: "pass"` shape. It also validates that the hardware log references the
benchmark id, dataset hash, spec batch id, generated timestamp, and MI300X GPU string.
It then writes `benchmark.json.sha256`, copies `methodology/hardware.log`, and re-renders
`artifacts/report.md`.

After `benchmark.json` exists and `python scripts/check_submission.py` passes the
benchmark contract, rebuild the Hugging Face upload bundles:

```bash
python scripts/export_static_space.py
python scripts/export_hf_space.py
```

The static export includes `data/benchmark.json`, `data/benchmark.json.sha256`, and
`methodology/hardware.log` automatically when they are present. The Gradio companion export
includes the full `artifacts/` directory.

## Acceptance Check

Submission-ready benchmark evidence requires:

- `hardware.gpu` names an AMD MI300X device.
- `hardware.hip` is present.
- `tolerance_check` is `"pass"`.
- `submission_ready` is `true`.
- Dataset hash matches the final dataset card shown in the webapp.
- `artifacts/methodology/hardware.log` exists and references the same benchmark id, dataset
  hash, spec batch id, generated timestamp, and MI300X GPU string.

## Current DevCloud Target

- Public IPv4: `165.245.141.127`
- Private IP: `10.128.0.2`
- Backend health URL: `http://165.245.141.127:8000/health`
