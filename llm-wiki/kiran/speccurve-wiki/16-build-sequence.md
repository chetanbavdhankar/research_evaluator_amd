# Build Sequence

Start with data and baseline, not UI. The UI only becomes valuable after the claim, specs, verifier, and benchmark are real enough to show.

## Practical Order

1. Lock product wording.
   - Use `D-001` and `D-002`.
   - Output: README headline and one-sentence pitch.

2. Create a one-page mock robustness report for user validation.
   - Use Berkeley or a clearly labeled mock if the final dataset is not selected.
   - Ask one reviewer/methods/statistics/instructor-type user whether the report is useful, honest, and trustworthy.
   - Output: `user-validation-notes.md`.

3. Select final paper, dataset, and claim.
   - Use `08-data-and-claim-contract.md`.
   - Output: decision record, local data, citation, license, target claim.
   - Stop if baseline is not plausible.

4. Build deterministic baseline.
   - Output: `baseline-result.json`.
   - Stop if baseline cannot be reproduced or explained.

5. Define specification schema and dimensions.
   - Output: `spec-space.json` with at least 50 early valid specs and path to 200+.
   - Keep rule-based generation first.

6. Build deterministic verifier rules.
   - Output: valid and invalid spec fixtures, verifier log.
   - Include missing column, outcome leakage, undocumented exclusion, claim change.

7. Add proposer/verifier agent calls with strict JSON.
   - Output: prompt logs, response logs, fallback path.
   - Agents must not block the deterministic demo.

8. Implement the first GPU-backed numerical operation.
   - Start with batched bootstrap unless the final claim makes permutation clearly better.
   - Output: CPU/GPU benchmark artifact following `09-gpu-and-benchmark-contract.md`.
   - Stop or redesign if MI300X is decorative.

9. Produce result table and provenance.
   - Output: approved spec results, rejected spec log, run metadata.

10. Build robustness surface.
   - Output: visual with baseline marker, approved specs, rejected spec summary, and point details.

11. Add explanation panel.
    - Output: cautious summary from deterministic result fields.
    - Run forbidden-language lint.

12. Add exportable report.
    - Output: Markdown or JSON robustness report with provenance and limitations.

13. Build app shell around the demo sequence.
    - Output: one route that follows `11-demo-contract.md`.
    - Do not add arbitrary upload, auth, or multi-paper workflows.

14. Publish the preferred demo surface.
    - Use Hugging Face Space unless a blocker is documented in `13-decision-log.md`.
    - Output: Space URL, public repo link, README, limitations, dataset citation, benchmark method.

15. Post build-in-public updates.
    - Update 1: "Why one p-value is not enough: the SpecCurve design."
    - Update 2: "MI300X benchmark: batched bootstrap robustness surface."
    - Tag LabLab and AMD accounts per `19-distribution-and-build-in-public-plan.md`.
    - Output: social links and AMD Developer Cloud/ROCm feedback note.

16. Prepare submission assets.
    - Output: cover image, video, slides, public repo, demo platform, app URL, README, screenshots.

17. Rehearse and harden.
    - Output: two-minute rehearsal, backup video, disclosed precomputed path, final lint pass.

## Work That Comes Later

- Arbitrary paper upload.
- Multiple datasets.
- Polished PDF export.
- Multi-user accounts.
- Fine-tuning.
- General statistical model library.
- Enterprise workflow.

## Build Stop Conditions

Stop and repair before continuing if:

- Dataset or claim is assumed but not decided.
- Baseline does not run.
- Agent outputs are not valid JSON.
- Invalid specs reach execution.
- GPU benchmark is unfair or unsupported.
- Demo cannot be explained in two minutes.
