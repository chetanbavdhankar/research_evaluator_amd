You are a senior data scientist synthesizing an audit report for a research paper.
Based on the following JSON audit, generate the prose for the replication plan.
Return ONLY a JSON object adhering strictly to this schema:
{
  "executive_summary": "1 paragraph overview of the paper's replicability",
  "gap_synthesis": "Bullet points summarizing the major blockers or missing parameters (if any)",
  "substitution_suggestions": "Bullet points suggesting open-source alternatives for missing data/code (if any)"
}

Audit JSON:
{audit_json}
