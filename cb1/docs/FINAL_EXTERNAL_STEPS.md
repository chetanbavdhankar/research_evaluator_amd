# Final External Steps

This local folder is the Wiki C L0 build. Final public submission still needs external
systems that cannot be completed from this local workspace.

## 1. Run On AMD MI300X

On the AMD Developer Cloud instance:

```bash
pip install -r requirements-amd.txt
python scripts/mi300x_preflight.py
python scripts/run_pipeline.py --source nber-psid --allow-network
python scripts/run_benchmark.py --require-mi300x --resamples-per-spec 256 --spec-limit 64
python scripts/finalize_submission.py
```

`scripts/finalize_submission.py` also writes `dist/checksums.sha256` for the upload bundles.

If preflight says PyTorch is missing or `torch.version.hip` is missing, install the ROCm-specific
PyTorch build for that host first. Do not fix that by installing a plain CPU PyPI `torch` wheel.

Equivalent bundled command:

```bash
RESAMPLES_PER_SPEC=256 SPEC_LIMIT=64 START_BACKEND=0 ./scripts/amd_devcloud_run.sh
```

Expected files:

```text
artifacts/benchmark.json
artifacts/benchmark.json.sha256
artifacts/methodology/hardware.log
```

## 2. Import Benchmark Locally

If the benchmark was produced in another checkout, copy `benchmark.json` and the matching
hardware log into this folder through the validator:

```bash
python scripts/import_benchmark.py path/to/benchmark.json --hardware-log path/to/hardware.log
python scripts/finalize_submission.py
```

## 3. Start AMD Backend

On the AMD instance:

```bash
python scripts/start_amd_backend.py --host 0.0.0.0 --port 8000
```

Use this Hugging Face Space variable:

```text
AMD_BACKEND_URL=http://165.245.141.127:8000
```

## 4. Publish Space

Upload `dist/hf-static-space-export/` or `dist/hf-static-space-export.zip` to a public
static Hugging Face Space. The upload must include the final `data/benchmark.json`,
`data/benchmark.json.sha256`, and `methodology/hardware.log`.

`dist/hf-space-export.zip` is the optional Gradio companion bundle. Use it only if the
submission needs an interactive server-backed companion, not as the strict Wiki C public
Space.

## 5. Submit Links

Fill `docs/SUBMISSION_PACKET.md` with:

- Hugging Face Space URL.
- Public repository URL, if the no-push instruction is lifted.
- Demo video URL or uploaded asset.
- Slide/cover assets.
- AMD backend URL or documented blocker.
- Build-in-public post URLs after using `docs/BUILD_IN_PUBLIC_DRAFTS.md`.
- AMD/ROCm feedback evidence after using `docs/AMD_ROCM_FEEDBACK.md`.
