# User Validation Plan

This is the smallest product-proof step before app implementation. It validates whether the reviewer-grade report is useful, honest, and legible to the first user.

## Target Respondent

One of:

- Statistically literate journal reviewer.
- Methods PhD.
- Statistician.
- Research methods instructor.
- Researcher who has reviewed public-data papers.

## Artifact To Show

Use one page. It can be:

- A Berkeley admissions teaching mock labeled as a teaching example.
- A final-dataset mock after the paper/dataset/claim decision exists.

Required sections:

- Paper/dataset/claim card.
- Baseline result.
- Specification count.
- Example invalid spec rejected by verifier.
- Robustness surface screenshot or sketch.
- Cautious conclusion.
- Limitations.
- Benchmark placeholder or real benchmark if available.

## Questions To Ask

1. Is this output useful for review or teaching?
2. Is the wording scientifically honest?
3. Would you attach this kind of report to peer review or use it in a methods class?
4. What would make you distrust it?
5. What missing detail would block you from using it?

## Pass Criteria

- Respondent can explain the conclusion in under two minutes.
- Respondent identifies at least one credible use or a clear reason it would not be useful.
- No wording is flagged as implying replication, proof, fraud, or scientific truth.
- Distrust triggers are recorded and mapped to wiki risks or feature contracts.

## Evidence Artifact

Save notes as:

```text
speccurve-wiki/user-validation-notes.md
```

If validation is deferred, record why in `13-decision-log.md` and keep the User-value gate open.
