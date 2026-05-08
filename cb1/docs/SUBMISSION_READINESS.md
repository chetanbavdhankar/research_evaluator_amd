# Submission Readiness

## Target

Submit SpecCurve L0 to the AMD Developer Hackathon as a Hugging Face Space backed by AMD MI300X evidence.

## Requirement Mapping

| Requirement | Current project support | Status |
| --- | --- | --- |
| Public Hugging Face Space in the event org | `space/README.md` and `space/index.html` implement the strict static Wiki C Space. | Ready to upload |
| Static Hugging Face upload bundle | `scripts/export_static_space.py` creates `dist/hf-static-space-export/` and `dist/hf-static-space-export.zip`. | Ready locally |
| Gradio companion bundle | `scripts/export_hf_space.py` creates `dist/hf-space-export/` and `dist/hf-space-export.zip`. | Ready locally |
| Hosted demo URL | Static Space entrypoint is implemented; Gradio companion is optional. | Ready after Space creation |
| AMD Developer Cloud / MI300X usage | ROCm/PyTorch benchmark and FastAPI backend are implemented. | Blocked until MI300X run creates `artifacts/benchmark.json`, `benchmark.json.sha256`, and `methodology/hardware.log` |
| Benchmark import/re-render path | `scripts/import_benchmark.py` validates a returned MI300X artifact plus hardware log, writes `benchmark.json.sha256`, and re-renders the report. | Ready locally |
| Public code repository | Folder is self-contained and ready to publish. | Not pushed by request |
| Application URL | Created after Space upload. | Pending external action |
| Cover image / video / slides | `assets/cover.svg`, `assets/cover.png`, `assets/demo-loop.gif`, `assets/slides.html`, `docs/PITCH_DECK.md`, and `docs/DEMO_SCRIPT.md` exist locally; final MP4 still pending. | Partially ready |
| Build in public extra challenge | Drafts exist in `docs/BUILD_IN_PUBLIC_DRAFTS.md`; posting and final links remain external. | Drafted locally |
| AMD/ROCm feedback note | Draft exists in `docs/AMD_ROCM_FEEDBACK.md`; final evidence values need the MI300X run. | Drafted locally |
| Wiki C LaLonde spec surface | Frozen NBER PSID source plus 240-spec matching/weighting grid. | Ready locally |

## DevCloud Endpoint

Current connection details from the AMD Developer Cloud UI:

- Public IPv4: `165.245.141.127`
- Private IP: `10.128.0.2`
- Intended backend URL: `http://165.245.141.127:8000`

Local connectivity checks from this workspace failed on ports `22`, `7860`, and `8000`, so the backend cannot be started remotely from here without additional access details or firewall changes.

## AMD Backend Run

On the AMD MI300X instance:

```bash
pip install -r requirements-amd.txt
python scripts/mi300x_preflight.py
python scripts/run_pipeline.py --source nber-psid --allow-network
python scripts/run_benchmark.py --require-mi300x --resamples-per-spec 256 --spec-limit 64
python scripts/start_amd_backend.py --host 0.0.0.0 --port 8000
```

The preflight is the authority for whether the remote Python environment is valid: it must
show PyTorch, HIP, an MI300-class GPU name, and a passing GPU tensor smoke test.

If a firewall is enabled:

```bash
sudo ufw allow 8000/tcp
```

The Hugging Face Space will read:

```text
AMD_BACKEND_URL=http://165.245.141.127:8000
```

## Hugging Face Space Settings

Create a Space under:

```text
lablab-ai-amd-developer-hackathon
```

Recommended settings:

- SDK: Static for strict Wiki C execution isolation
- Visibility: Public for final submission
- Tag: `amd-hackathon-2026`

Use the Gradio bundle only as an optional interactive companion. The strict public demo path
should be the static bundle because Wiki C requires no server-side execution or backend API calls
inside the Hugging Face Space.

## Final Gate

The package is Wiki C L0 software-ready locally now. It is final-submission ready only after:

1. `artifacts/benchmark.json`, `artifacts/benchmark.json.sha256`, and `artifacts/methodology/hardware.log` are generated on AMD MI300X.
2. `python scripts/import_benchmark.py path/to/benchmark.json --hardware-log path/to/hardware.log` passes locally if the artifact was generated elsewhere.
3. `python scripts/finalize_submission.py --check-amd-socket` passes or records only documented external URL blockers.
4. The Space can reach the AMD backend health endpoint.
5. The live Space URL is submitted on lablab.
6. A public code repository URL is supplied.
7. Presentation assets are added.

Local presentation assets now included:

- `assets/cover.svg`
- `assets/cover.png`
- `assets/demo-loop.gif`
- `assets/slides.html`
- `docs/PITCH_DECK.md`
- `docs/DEMO_SCRIPT.md`
- `docs/SUBMISSION_PACKET.md`
- `docs/BUILD_IN_PUBLIC_DRAFTS.md`
- `docs/AMD_ROCM_FEEDBACK.md`
