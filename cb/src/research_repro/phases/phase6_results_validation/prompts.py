EVALUATE_DISCREPANCY_PROMPT = """You are analyzing a reproducibility discrepancy.
The original paper claimed the following result:
{reported_result}

The replicated pipeline produced the following result:
{reproduced_result}

This represents a discrepancy.
Review the following Pipeline Audit Logs to identify likely causes:
{audit_logs}

Provide an explanation, classify it as "explained", "partially_explained", or "unexplained", and list candidate causes.
"""

ASSESS_CLAIM_PROMPT = """The original paper made the following claim in its conclusion:
{claim}

The reproduced results are:
{results_summary}

Assess whether the reproduced results support the claim.
Classify as "supported", "partially_supported", "not_supported", or "cannot_assess".
Provide a rationale.
"""

GENERATE_NARRATIVE_PROMPT = """Generate the executive summary, overall reproducibility score, and recommendations for this paper.

Original Paper Artifact:
{pka}

Results Comparison Summary:
{comparisons}

Discrepancies:
{discrepancies}

Claims Assessed:
{claims}

Determine the overall score based on the results and provide an executive summary and actionable recommendations.
"""
