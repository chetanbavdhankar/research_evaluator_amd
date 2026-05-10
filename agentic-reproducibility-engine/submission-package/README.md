# Final Submission Package

This folder packages the Agentic Reproducibility Engine for the AMD Developer Hackathon submission.

The live lablab.ai page asks for:

- Project title.
- Short description.
- Long description.
- Technology and category tags.
- Cover image.
- Video presentation.
- Slide presentation.
- Public GitHub repository.
- Demo application platform.
- Application URL.

The AMD/Hugging Face hackathon page also emphasizes publishing the final project as a Hugging Face Space and submitting that Space link on lablab.

## Upload Map

| lablab field | Use this artifact |
| --- | --- |
| Project Title | `SUBMISSION_FORM.md` |
| Short Description | `SUBMISSION_FORM.md` |
| Long Description | `SUBMISSION_FORM.md` |
| Technology & Category Tags | `SUBMISSION_FORM.md` |
| Cover Image | `assets/cover-image.png` |
| Video Presentation | Record using `video/VIDEO_SCRIPT.md` and `demo/DEMO_RUNBOOK.md` |
| Slide Presentation | `presentation/agentic-reproducibility-engine-slides.pdf` |
| Public GitHub Repository | `https://github.com/chetanbavdhankar/research_evaluator_amd` |
| Demo Application Platform | Hugging Face Static Space + AMD Developer Cloud backend |
| Application URL | Fill in after the HF Space is live |

## Submission-Ready Defaults

- Track: `AI Agents & Agentic Workflows`
- Product name: `Agentic Reproducibility Engine`
- Public code path: `agentic-reproducibility-engine/`
- AMD deployment path: `agentic-reproducibility-engine/deploy-amd-hf/`
- Frontend: static `index.html`, suitable for Hugging Face Static Space hosting.
- Backend: FastAPI agent API on AMD GPU host.
- Model target: `Qwen/Qwen3.5-27B` via vLLM on ROCm.

## Remaining Manual Items

These require external accounts or live infrastructure:

- Deploy the static Hugging Face Space.
- Deploy the AMD backend and connect the Space with `?api=https://<amd-api-host>`.
- Record a video presentation under 5 minutes.
- Review the generated slide PDF.
- Upload the cover image.
- Add live URLs to `SUBMISSION_FORM.md` before pasting into lablab.
- Optional extra challenge: publish two build-in-public posts using `BUILD_IN_PUBLIC.md`.
