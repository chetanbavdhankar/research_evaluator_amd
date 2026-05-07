# Distribution And Build-In-Public Plan

Official source checked on 2026-05-05: https://lablab.ai/ai-hackathons/amd-developer

The official page makes distribution part of the product strategy, not an afterthought. SpecCurve should use the hackathon's Hugging Face and build-in-public surfaces to make the project easier to try, easier to judge, and easier to remember.

Metadata:

```yaml
confidence: high
source: https://lablab.ai/ai-hackathons/amd-developer
last_verified: 2026-05-05
status: active
decision_id_optional: D-009
```

## Default Demo Platform

Use Hugging Face Space as the preferred demo platform unless a blocker appears.

Why:

- The official page describes Hugging Face as the model hub and deployment layer for the hackathon.
- It instructs teams to publish the final project as a Space in the event organization and submit the Space link.
- The Hugging Face special prize rewards the Space with the most likes in the event organization.
- A Space is public, judge-friendly, and aligned with the submission requirement for demo platform and app URL.

Allowed blockers:

- Space cannot access required GPU/runtime path.
- Demo requires private AMD Developer Cloud resources that cannot be exposed safely.
- Dataset or benchmark artifact cannot be packaged within Space constraints.
- Space reliability is worse than another public hosted app during rehearsal.

If a blocker appears, record it in `13-decision-log.md` and provide an alternate app URL plus a public Hugging Face project page or technical walkthrough if feasible.

## Build-In-Public Updates

The official extra challenge asks for at least two technical updates, tagged to LabLab and AMD accounts, plus meaningful feedback about ROCm, AMD Developer Cloud, or APIs, and open-source publication or a technical walkthrough.

### Update 1 - Product Design

Working title:

```text
Why one p-value is not enough: the SpecCurve design
```

Content:

- One public paper and one target claim.
- Why specification choices matter.
- Why SpecCurve is not replication.
- Proposer/verifier/explainer roles.
- Screenshot or sketch of paper card, verifier panel, and robustness surface.
- Link to repo or wiki page if public.

Safe phrasing:

```text
SpecCurve performs GPU-scale specification robustness analysis: one public claim, many defensible analysis specifications, verifier-checked before execution.
```

Do not claim:

- Final benchmark speedup before logs exist.
- Final dataset if not selected.
- Proof that a paper is right or wrong.

### Update 2 - AMD Technical Proof

Working title:

```text
MI300X benchmark: batched bootstrap robustness surface
```

Content:

- Final or prototype dataset/claim.
- Approved spec count and resampling count.
- Batched bootstrap operation.
- CPU/GPU fairness rules: same data, same specs, same resamples, tolerance check.
- Hardware/runtime metadata.
- Speedup only if measured.
- What worked and what was hard about ROCm/PyTorch on AMD Developer Cloud.

Safe phrasing:

```text
The benchmark compares the same robustness workload on CPU and AMD MI300X. The surface uses generated benchmark artifacts, not hand-edited numbers.
```

## Required Tags And Accounts

For the build-in-public extra challenge, tag one LabLab account and one AMD account on each technical update:

| Platform | LabLab tag | AMD tag |
|---|---|---|
| X | `@lablab` | `@AIatAMD` |
| LinkedIn | `lablab.ai` | `AMD Developer` |

Preferred posting pattern:

- Post each update on X if the team has an active account there.
- Cross-post to LinkedIn if the project needs a more professional reviewer/methods audience.
- Include the Hugging Face Space link after it is live.
- Include the public GitHub link once the README and limitations are safe.

## AMD Developer Cloud / ROCm Feedback Note

Prepare a short feedback note for the extra challenge. Keep it concrete and evidence-backed.

Template:

```text
We used AMD Developer Cloud and ROCm/PyTorch to run [operation] for SpecCurve.

What worked:
- [Example: MI300X access path, PyTorch HIP detection, large-batch memory headroom.]

What was confusing or slow:
- [Example: dependency setup, version matching, logging hardware metadata, Space-vs-cloud workflow.]

What we would improve:
- [Example: clearer starter template for PyTorch ROCm benchmarking, recommended logging snippet, Space deployment guidance for AMD-backed workloads.]

Evidence:
- Benchmark artifact: [path/link]
- Hardware log: [path/link]
- Space: [link]
- Repo: [link]
```

Do not submit generic praise. The feedback should be useful to AMD/LabLab even if some parts of the build were difficult.

## Distribution Checklist

- Join the event's Hugging Face organization.
- Create the SpecCurve Space.
- Add README, limitations, dataset citation, and benchmark method.
- Make precomputed/live status visible in the UI.
- Add public GitHub repo link.
- Add app URL to LabLab submission.
- Post Update 1 after product design is stable.
- Post Update 2 after benchmark artifact exists.
- Record social links in submission notes.
- Record AMD Developer Cloud/ROCm feedback note.

## Failure Modes

| Failure | Mitigation |
|---|---|
| Space is live but benchmark is unsupported. | Label benchmark as pending or prototype; do not claim speedup. |
| Social update overclaims before evidence. | Run `14-quality-lint.md` before posting. |
| GitHub repo exposes messy private notes or secrets. | Review repo before public link; never commit credentials. |
| HF Space cannot run full workload. | Show precomputed robustness artifact and a smaller live benchmark with disclosure. |
| Build-in-public distracts from dataset/baseline. | Use two focused updates only; do not turn posting into the work. |
