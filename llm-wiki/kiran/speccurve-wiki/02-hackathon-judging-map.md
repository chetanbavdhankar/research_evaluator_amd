# Hackathon Judging Map

Official source checked on 2026-05-05: https://lablab.ai/ai-hackathons/amd-developer

The LabLab page lists four judging criteria: Application of Technology, Presentation, Business Value, and Originality. It also asks for basic project information, cover image, video presentation, slide presentation, public GitHub repository, demo application platform, and application URL. The event schedule shown on the page is April 25, 2026 start, May 15, 2026 end, and May 23, 2026 winners announcement.

## Criteria Mapping

| Criterion | Official meaning | SpecCurve claim | Demo evidence required |
|---|---|---|---|
| Application of Technology | Chosen model(s) integrated effectively into the solution. | Agents create and verify analysis plans; AMD MI300X executes the numerical batch. | ROCm/PyTorch device metadata, MI300X label, approved spec batch, CPU baseline, GPU runtime, throughput, speedup formula, logs. |
| Presentation | Clarity and effectiveness of project presentation. | One paper, one claim, one robustness surface. | Two-minute flow, paper/dataset card, baseline marker, verifier rejection, AMD panel, cautious conclusion. |
| Business Value | Practical value and fit into business areas. | Reviewers and methods instructors can turn manual robustness checking into reusable reports. | Exportable report, time-saved story, first-user workflow, limitations and provenance. |
| Originality | Uniqueness, creativity, and demonstrated behavior. | Combines agent-generated specs, verifier safeguards, GPU-scale execution, and traceable robustness surface. | Rejected invalid spec, structured JSON specs, every point linked to provenance, not a generic paper chatbot. |

Metadata:

```yaml
confidence: high
source: https://lablab.ai/ai-hackathons/amd-developer
last_verified: 2026-05-05
status: active
```

## Submission Asset Checklist

Official checklist:

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
- Submission deadline checked in the Event Schedule tab in local timezone.

SpecCurve-specific assets:

- Architecture diagram showing agents, verifier, statistics engine, MI300X batch, and report output.
- Hugging Face Space as preferred demo platform unless a documented blocker appears.
- Screenshot of paper/dataset card.
- Screenshot of verifier rejection.
- Screenshot of AMD proof panel.
- Screenshot of robustness surface.
- README with setup, dataset citation, benchmark method, limitations, and non-replication framing.
- Benchmark logs with hardware, runtime, warmup policy, and CPU/GPU comparability.
- Two build-in-public technical updates with LabLab and AMD tags.
- AMD Developer Cloud/ROCm feedback note.
- Backup demo video and precomputed run disclosure if used.

## Distribution Tactic

Use the hackathon distribution surface as part of the winning strategy:

- Publish the demo as a Hugging Face Space in the event organization unless blocked.
- Submit the Space link as the application URL.
- Post two technical updates: product design first, benchmark proof second.
- Include concrete feedback on AMD Developer Cloud, ROCm, or model/API experience.

See `19-distribution-and-build-in-public-plan.md`.

## Judge-Facing One-Liner

```text
SpecCurve turns one public research claim into a verifier-checked, MI300X-executed robustness surface that a reviewer can inspect and export.
```

## Losing Conditions By Criterion

| Criterion | How SpecCurve loses | Prevention |
|---|---|---|
| Application of Technology | GPU is a logo around Python loops. | Pass `09-gpu-and-benchmark-contract.md`. |
| Presentation | Demo becomes a statistics lecture. | Follow `11-demo-contract.md`. |
| Business Value | User is "all researchers." | Keep first user as reviewer/methods instructor. |
| Originality | Looks like a paper chatbot. | Make verifier and robustness surface the hero. |
