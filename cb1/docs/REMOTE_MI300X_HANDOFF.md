# Remote MI300X Handoff

Use this from the Kali terminal that can SSH into the AMD MI300X/ROCm droplet. This path
does not require GitHub push access.

## 1. Upload The Local Submission Zip

From Kali, set these values:

```bash
export AMD_HOST=165.245.141.127
export AMD_USER=root
export LOCAL_ZIP=/path/to/speccurve-l0-hf-space-submission.zip
export REMOTE_DIR=/root/speccurve-l0-hf-space
```

If the droplet uses a non-root user, change `AMD_USER`.

Upload and unpack:

```bash
scp "$LOCAL_ZIP" "$AMD_USER@$AMD_HOST:/tmp/speccurve-l0-hf-space-submission.zip"
ssh "$AMD_USER@$AMD_HOST" "rm -rf '$REMOTE_DIR' && mkdir -p '$REMOTE_DIR' && unzip -q /tmp/speccurve-l0-hf-space-submission.zip -d '$REMOTE_DIR'"
```

## 2. Verify ROCm PyTorch Before Running The Benchmark

```bash
ssh "$AMD_USER@$AMD_HOST" "cd '$REMOTE_DIR' && python3 -m venv .venv && . .venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -r requirements-amd.txt && python scripts/mi300x_preflight.py"
```

Expected result:

```text
preflight_status=pass
```

The preflight must show:

- PyTorch import works.
- `torch.version.hip` is populated.
- PyTorch sees an AMD MI300-class GPU.
- The GPU tensor smoke test passes.

If preflight fails because PyTorch is missing or HIP is missing, activate the same virtualenv
and install the ROCm-specific PyTorch build for that droplet image, then re-run preflight.
Do not install a plain CPU PyPI `torch` wheel.

## 3. Run The Full AMD Evidence Build

```bash
ssh "$AMD_USER@$AMD_HOST" "cd '$REMOTE_DIR' && . .venv/bin/activate && RESAMPLES_PER_SPEC=256 SPEC_LIMIT=64 START_BACKEND=0 ./scripts/amd_devcloud_run.sh"
```

Expected files on the droplet:

```text
artifacts/benchmark.json
artifacts/benchmark.json.sha256
artifacts/methodology/hardware.log
dist/checksums.sha256
dist/hf-static-space-export.zip
dist/hf-space-export.zip
dist/speccurve-l0-hf-space-submission.zip
```

The final readiness output should be `ready` or `ready_with_external_blocker` only because
the backend/socket and hosted Space URL are not checked from inside the package run.

## 4. Pull Back The Evidence Bundle

From Kali:

```bash
mkdir -p ./speccurve-mi300x-evidence
scp "$AMD_USER@$AMD_HOST:$REMOTE_DIR/artifacts/benchmark.json" ./speccurve-mi300x-evidence/
scp "$AMD_USER@$AMD_HOST:$REMOTE_DIR/artifacts/benchmark.json.sha256" ./speccurve-mi300x-evidence/
scp "$AMD_USER@$AMD_HOST:$REMOTE_DIR/artifacts/methodology/hardware.log" ./speccurve-mi300x-evidence/
scp "$AMD_USER@$AMD_HOST:$REMOTE_DIR/dist/checksums.sha256" ./speccurve-mi300x-evidence/
scp "$AMD_USER@$AMD_HOST:$REMOTE_DIR/dist/hf-static-space-export.zip" ./speccurve-mi300x-evidence/
scp "$AMD_USER@$AMD_HOST:$REMOTE_DIR/dist/hf-space-export.zip" ./speccurve-mi300x-evidence/
```

## 5. Optional Backend

If you want the optional FastAPI status backend running on the droplet:

```bash
ssh "$AMD_USER@$AMD_HOST" "cd '$REMOTE_DIR' && . .venv/bin/activate && nohup python scripts/start_amd_backend.py --host 0.0.0.0 --port 8000 > backend.out 2> backend.err &"
```

Then check:

```bash
curl "http://$AMD_HOST:8000/health"
```

If it fails, open port `8000/tcp` in the droplet firewall or cloud firewall.

## 6. What To Paste Back

Paste these outputs back into Codex:

```bash
ssh "$AMD_USER@$AMD_HOST" "cd '$REMOTE_DIR' && . .venv/bin/activate && python scripts/mi300x_preflight.py"
ssh "$AMD_USER@$AMD_HOST" "cd '$REMOTE_DIR' && python - <<'PY'
import json
from pathlib import Path
b=json.loads(Path('artifacts/benchmark.json').read_text())
print(json.dumps({
  'benchmark_id': b.get('benchmark_id'),
  'gpu': b.get('hardware', {}).get('gpu'),
  'hip': b.get('hardware', {}).get('hip'),
  'torch': b.get('hardware', {}).get('torch'),
  'speedup': b.get('speedup'),
  'tolerance_check': b.get('tolerance_check'),
  'submission_ready': b.get('submission_ready'),
}, indent=2))
PY"
```
