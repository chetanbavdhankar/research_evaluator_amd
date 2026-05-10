# Final Submission Checklist

## Required By lablab.ai

- [ ] Project Title: `Agentic Reproducibility Engine`
- [ ] Short Description: paste from `SUBMISSION_FORM.md`
- [ ] Long Description: paste from `SUBMISSION_FORM.md`
- [ ] Technology & Category Tags: paste from `SUBMISSION_FORM.md`
- [ ] Cover Image: upload `assets/cover-image.png`
- [ ] Video Presentation: record with `video/VIDEO_SCRIPT.md`
- [ ] Slide Presentation: upload `presentation/agentic-reproducibility-engine-slides.pdf`
- [ ] Public GitHub Repository: `https://github.com/chetanbavdhankar/research_evaluator_amd`
- [ ] Demo Application Platform: `Hugging Face Static Space + AMD Developer Cloud backend`
- [ ] Application URL: add final Space URL

## Recommended For AMD/Hugging Face Judging

- [ ] Hugging Face Space is live and reachable.
- [ ] AMD backend `/health` returns model profile.
- [ ] vLLM serves the Hugging Face model through `/v1/models`.
- [ ] One audit run completes from the public UI.
- [ ] UI visibly streams trace events and final report.
- [ ] `python scripts/run_evals.py --runtime env --k 1` passes on the AMD host.
- [ ] Capture GPU/ROCm proof with `deploy-amd-hf/scripts/check_amd_readiness.py --strict`.
- [ ] Keep vLLM private; expose only the agent API.

## Optional Build In Public Challenge

- [ ] Post technical update 1 and tag lablab + AMD.
- [ ] Post technical update 2 and tag lablab + AMD.
- [ ] Add meaningful AMD/ROCm feedback from `BUILD_IN_PUBLIC.md`.
- [ ] Keep GitHub repo public.

## Evidence To Keep Handy

- GitHub repo URL.
- Hugging Face Space URL.
- AMD backend URL.
- `/health` JSON.
- Eval output.
- Screenshot of dashboard trace.
- Screenshot of final report.
- vLLM startup log.
- ROCm/GPU readiness output.
