# Agent Contracts

Agents are constrained workers. They do not compute statistics, invent results, invent data, or decide whether a paper is true.

## Shared Rules

- Inputs must be structured JSON or cited metadata.
- Outputs must be strict JSON matching the schema.
- Deterministic code owns validation, execution, and numerical results.
- If an agent fails or returns invalid JSON, use the deterministic fallback.
- Every prompt and response must be logged.

## A01 - Proposer Agent

Allowed inputs:

```json
{
  "dataset_schema": {},
  "target_claim": {},
  "allowed_dimensions": {},
  "forbidden_rules": [],
  "max_specs": 20
}
```

Forbidden behavior:

- Invent columns.
- Change the claim.
- Add undocumented exclusions.
- Suggest causal claims not supported by the design.
- Produce prose instead of JSON.

Output JSON schema:

```json
{
  "agent": "proposer",
  "specs": [
    {
      "spec_id": "string",
      "model_family": "string",
      "outcome": "string",
      "predictor": "string",
      "covariates": ["string"],
      "exclusion_rule": "string",
      "transforms": {},
      "resampling": {},
      "rationale": "string",
      "confidence": "high|medium|low"
    }
  ]
}
```

Acceptance tests:

- Reject response if any column is absent from schema.
- Reject response if target outcome or predictor changes.
- Reject response if not valid JSON.
- Require rationale for every spec.

Fallback:

- Use deterministic rule-grid specs from allowed dimensions.

## A02 - Verifier Agent

Allowed inputs:

```json
{
  "spec": {},
  "dataset_schema": {},
  "target_claim": {},
  "hard_rule_results": [],
  "soft_rules": []
}
```

Forbidden behavior:

- Override a failed hard rule.
- Approve a spec with outcome leakage.
- Approve a spec that changes the target claim.
- Invent statistical results.
- Declare a study true, false, fraudulent, or replicated.

Output JSON schema:

```json
{
  "agent": "verifier",
  "spec_id": "string",
  "status": "approved|rejected",
  "rule_results": [
    {
      "rule_id": "string",
      "status": "pass|fail|warn",
      "reason": "string"
    }
  ],
  "final_reason": "string",
  "repair_optional": "string"
}
```

Acceptance tests:

- Missing column fixture must be rejected.
- Outcome-as-covariate fixture must be rejected.
- Undocumented exclusion fixture must be rejected.
- Claim-changing fixture must be rejected.
- Valid baseline-like spec must be approved or warned, not rejected without reason.

Fallback:

- Deterministic verifier rules decide status; agent explanation is omitted or replayed from cached valid response.

## A03 - Explainer Agent

Allowed inputs:

```json
{
  "claim": {},
  "result_summary": {},
  "sensitivity_drivers": [],
  "limitations": [],
  "forbidden_phrases": []
}
```

Forbidden behavior:

- Say "replicated," "proved wrong," "proved true," or "solved the replication crisis."
- Invent drivers not in `sensitivity_drivers`.
- Omit major limitations.
- Use causal certainty unless the claim contract permits it.

Output JSON schema:

```json
{
  "agent": "explainer",
  "result_label": "robust|fragile|mixed|inconclusive",
  "summary": "string",
  "key_sensitivity_drivers": ["string"],
  "limitations": ["string"],
  "safe_demo_sentence": "string"
}
```

Acceptance tests:

- Forbidden phrase lint passes.
- Summary references computed counts or labels only.
- Limitations are non-empty.
- Result label matches deterministic summary thresholds.

Fallback:

- Use deterministic template: "Under the tested specification space, the result is [label]. The main sensitivity driver is [driver]. This is not replication and does not prove truth or falsehood."

## A04 - Report-Writer Agent Optional

Allowed inputs:

```json
{
  "metadata": {},
  "baseline": {},
  "spec_summary": {},
  "verifier_summary": {},
  "benchmark": {},
  "robustness_summary": {},
  "limitations": []
}
```

Forbidden behavior:

- Invent assets, citations, logs, or benchmark numbers.
- Remove precomputed/live disclosure.
- Convert cautious conclusion into a verdict.

Output JSON schema:

```json
{
  "agent": "report_writer",
  "title": "string",
  "sections": [
    {
      "heading": "string",
      "body": "string",
      "source_fields": ["string"]
    }
  ],
  "missing_evidence": ["string"]
}
```

Acceptance tests:

- Every section lists source fields.
- Missing evidence is explicit.
- Report includes claim, dataset, verifier, benchmark, surface summary, limitations.

Fallback:

- Export deterministic Markdown assembled from JSON artifacts.
