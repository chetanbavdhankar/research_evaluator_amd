# Prompt Library

Use these prompts with structured inputs. Replace bracketed fields with JSON or cited metadata. Do not let prompts invent missing facts.

## Ingest A New Research Paper

```text
You are ingesting a paper for SpecCurve.

Input:
[paper metadata, abstract, methods excerpt, dataset link, citation, license notes]

Task:
Extract only source-supported entities using the SpecCurve schema: Paper, Dataset, Claim candidates, Specification dimensions, limitations, and open questions.

Rules:
- Do not invent data, claims, sample sizes, or results.
- Mark every entity with confidence, source, last_verified, and status.
- If the dataset/license/baseline is unclear, mark it uncertain.

Return strict JSON:
{
  "paper": {},
  "datasets": [],
  "claim_candidates": [],
  "specification_dimensions": [],
  "limitations": [],
  "open_questions": []
}
```

## Extract A Target Claim

```text
Given the paper and dataset metadata below, propose up to three narrow target claims for SpecCurve.

Input:
[paper metadata, dataset schema, source-supported reported results]

Rules:
- Each claim must identify outcome, predictor, expected direction, and what it does not prove.
- Do not use replication, proof, fraud, or truth-verdict language.
- Prefer claims that can support 50-200 defensible specifications.

Return strict JSON:
{
  "claim_candidates": [
    {
      "plain_english_claim": "",
      "outcome": "",
      "predictor": "",
      "expected_direction": "",
      "what_this_does_not_prove": "",
      "why_suitable": "",
      "risks": [],
      "confidence": "high|medium|low"
    }
  ]
}
```

## Generate Specifications

```text
You are the SpecCurve proposer agent.

Input:
[dataset schema, target claim, allowed dimensions, forbidden rules, max_specs]

Rules:
- Stay inside allowed dimensions.
- Do not invent columns.
- Do not change the claim.
- Provide a rationale for every spec.
- Return JSON only.

Output schema:
{
  "specs": [
    {
      "spec_id": "",
      "model_family": "",
      "outcome": "",
      "predictor": "",
      "covariates": [],
      "exclusion_rule": "",
      "transforms": {},
      "resampling": {},
      "rationale": "",
      "confidence": "high|medium|low"
    }
  ]
}
```

## Verify Specifications

```text
You are the SpecCurve verifier agent.

Input:
[one spec JSON, dataset schema, target claim, hard rule results, soft rules]

Rules:
- If any hard rule failed, status must be rejected.
- Reject missing columns, outcome leakage, undocumented exclusions, small sample, invalid model family, or claim changes.
- Do not compute or invent results.
- Return JSON only.

Output schema:
{
  "spec_id": "",
  "status": "approved|rejected",
  "rule_results": [
    {
      "rule_id": "",
      "status": "pass|fail|warn",
      "reason": ""
    }
  ],
  "final_reason": "",
  "repair_optional": ""
}
```

## Summarize A Robustness Surface

```text
You are the SpecCurve explainer agent.

Input:
[claim, deterministic result summary, sensitivity drivers, limitations, forbidden phrases]

Rules:
- Explain only computed results.
- Do not say replicated, proved, true, false, fraud, or solved.
- State uncertainty and limitations.
- Use "under the tested specification space."

Return strict JSON:
{
  "result_label": "robust|fragile|mixed|inconclusive",
  "summary": "",
  "key_sensitivity_drivers": [],
  "limitations": [],
  "safe_demo_sentence": ""
}
```

## Update Wiki After A Build Session

```text
You are updating the SpecCurve wiki after implementation work.

Input:
[changed files, test results, benchmark logs, screenshots, decisions, blockers]

Task:
List wiki updates required across decisions, feature contracts, eval gates, risks, and source map.

Rules:
- Separate facts, decisions, assumptions, and open questions.
- Mark confidence/status/last_verified.
- Do not convert failed checks into success claims.

Return:
1. Pages to update.
2. New or changed decisions.
3. Evidence artifacts.
4. Open questions.
```

## Run A Contradiction Check

```text
Compare the proposed change against the SpecCurve wiki.

Input:
[proposed claim or decision, relevant wiki excerpts]

Task:
Identify contradictions, superseded assumptions, unsupported AMD claims, overclaiming, and missing metadata.

Return:
{
  "contradictions": [],
  "supersession_needed": [],
  "unsupported_claims": [],
  "safe_rewrite": "",
  "required_wiki_updates": []
}
```

## Prepare A Judge-Facing Explanation

```text
Create a 30-second judge-facing explanation of SpecCurve.

Inputs:
[selected paper/claim, spec count, verifier result, benchmark summary, robustness result, limitations]

Rules:
- Use the phrase "GPU-scale specification robustness analysis."
- Do not claim replication or proof.
- Mention agents, verifier, MI300X, and robustness surface.
- If benchmark data is missing, say "planned" or omit speedup.

Return:
{
  "spoken_version": "",
  "slide_version": "",
  "unsafe_phrases_removed": []
}
```
