# EVAL: agentic-reproducibility

## Software 3.0 Framing

The prompts, context payloads, tool requests, and trace events are treated as
first-class software. A run is not successful because the UI looks plausible or
the report reads well. A run is successful only when the system produces
versioned artifacts that can be graded.

This suite follows eval-driven development:

- Define expected behavior before changing prompts or orchestration.
- Keep golden cases in data, not hidden in the implementation.
- Prefer deterministic code graders over vibes.
- Track pass@k for stochastic runtimes and pass^k for release stability.
- Convert production failures into fixed regression rows.

## Capability Evals

1. Explicit paper with blocked live evidence fails closed.
   - Extracts arXiv, DOI, GitHub, and dataset identifiers.
   - Executes every required agent turn.
   - Records model artifacts, tool requests, tool validation, and trace events.
   - Scores from resolver output and degrades the audit when evidence is skipped.
   - Triggers verifier repair when high-autonomy unresolved gaps remain.

2. Unsupported claims produce a missing-evidence report.
   - Does not invent paper identity, repository, or dataset evidence.
   - Preserves concrete resolver gaps.
   - Blocks code/data planning at the selected autonomy level.
   - Produces a final report with provenance and gap disclosure.

3. Low autonomy gates external and code/data tool classes.
   - Blocks live resolvers through the orchestrator policy.
   - Blocks code/data planning.
   - Still completes the audit as a fail-closed report.

## Per-Agent Contract Graders

- Planner: receives autonomy policy, emits a model-backed turn, routes to paper
  understanding.
- Paper reader: calls parsing, extracts claims, source refs, and identifiers.
- Evidence retriever: requests resolver tools and records resolver status for
  arXiv, DOI, GitHub, and dataset sources.
- Reproducibility auditor: calls the deterministic scorer, emits bounded score,
  decision, rubric, and expected gaps.
- Experiment planner: converts scorecard gaps into a replication plan and
  carries blocked items forward.
- Code/data agent: respects autonomy gates, requires sandboxing, and generates
  commands only when allowed.
- Verifier/critic: emits an explicit decision, keeps unresolved gaps visible,
  and requests repair only when policy permits it.
- Report agent: produces required report sections, provenance counts, and no
  placeholder/demo evidence.

## Overall Audit Success

An audit passes only if:

- The manifest completes.
- Required agents, tools, and trace event classes are present.
- Final decision matches the expected case outcome.
- Missing evidence causes a degraded decision instead of a pass.
- Report sections are complete.
- Banned placeholder strings are absent from the full run payload.

## Run

```bash
python scripts/run_evals.py --k 1
python scripts/run_evals.py --k 3
python scripts/run_evals.py --runtime env --k 3
```

## Release Gate

- Mock runtime: pass^3 must be 100%.
- Env/Qwen/Gemini runtime: pass@3 should be at least 90%, and every failure must
  include a trace-linked reason before submission.
- Any prompt, tool policy, report template, resolver, or graph change should run
  this suite before being treated as judge-ready.
