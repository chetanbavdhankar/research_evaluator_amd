# Operating Manual

## Purpose

This wiki lets humans and LLM agents build SpecCurve without re-litigating the product. It separates facts, decisions, assumptions, open questions, and superseded ideas.

## Working Contract

1. Read `README.md`, `01-product-thesis.md`, and the specific contract page before changing the app.
2. Check `13-decision-log.md` before reviving an old framing, feature, dataset, or architecture.
3. Use `04-knowledge-schema.md` for entity names, relationship names, metadata, and status.
4. Verify source-backed claims in `03-source-map.md` before using them in submission copy.
5. If implementation reality differs from this wiki, update the wiki in the same session.

## What LLM Agents May Do

- Propose machine-readable analysis specifications inside allowed dimensions.
- Verify proposed specifications against written rules.
- Explain why a specification was approved or rejected.
- Summarize computed robustness results with limitations.
- Draft reports, submission copy, and judge-facing explanations from logged evidence.

## What LLM Agents Must Not Do

- Invent datasets, paper claims, benchmark numbers, citations, or statistical results.
- Change the target claim to make a result more dramatic.
- Compute statistics in prose.
- Approve specifications that deterministic rules reject.
- Use "replication" framing unless independent new data is actually used.
- Hide uncertainty, cached runs, failed checks, or benchmark limitations.

## Wiki Update Rules

When adding or changing knowledge, include:

```yaml
confidence: high | medium | low
source: path-or-url
last_verified: YYYY-MM-DD
status: active | superseded | uncertain | rejected
owner_optional:
decision_id_optional:
```

If a new decision contradicts an old one:

1. Add a decision record in `13-decision-log.md`.
2. Mark the old claim `superseded`.
3. Link the old and new claims with `supersedes` / `superseded_by`.
4. Update affected feature, agent, demo, and risk contracts.

## Drift Prevention

- Keep one paper, one dataset, one target claim, one visual centerpiece, and one real AMD benchmark until the MVP is complete.
- Prefer deleting scope over adding abstractions.
- Use deterministic checks before LLM judgment.
- Record benchmark evidence before writing AMD claims.
- Treat Berkeley admissions as a teaching example, not the final dataset decision.

## Stop Conditions

Stop implementation and repair the wiki if:

- The final dataset is being assumed but no decision record exists.
- A feature lacks acceptance criteria.
- The GPU benchmark is not comparable to CPU.
- Any public copy says or implies that SpecCurve proves truth, fraud, or replication.
- A decision has no source, confidence, status, or last verification date.
