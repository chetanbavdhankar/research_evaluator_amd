# Phase 6: Results Validation and Report Generation

## Purpose

This phase takes the Analysis Results Package from Phase 5 and compares it systematically against the results reported in the paper. It produces a structured, honest, and actionable reproducibility report that clearly communicates what was reproduced, what was not, why discrepancies exist, and what their implications are for the paper's claims.

This phase does not judge the quality of the original research. It assesses the degree to which the research can be independently reproduced given what was described, and it provides evidence to support that assessment.

---

## Core Principle: Evidence-Based Assessment, Not Binary Pass/Fail

Reproducibility is not binary. A result may be exactly reproduced, approximately reproduced within statistical noise, reproduced in direction but not magnitude, or not reproduced at all. Each of these outcomes carries different implications for the paper's credibility and the replication's validity.

The goal is to produce an assessment that is:
- **Precise:** specific about which results match and which do not
- **Calibrated:** honest about whether discrepancies are explained by known factors (missing seeds, hardware differences, ambiguous preprocessing) or are unexplained
- **Actionable:** clear about what a future replicator would need to do differently to close any remaining gaps

---

## Establishing the Comparison Baseline

Before comparing results, establish what the comparison target is. This comes from:

1. **The PKA's Results section:** the exact numbers, tables, and figures reported in the paper
2. **The Reproducibility Target defined in Phase 3:** whether exact, numerical, statistical, or qualitative agreement is expected

For each reported result in the PKA, create a **Result Record** containing:
- The result as reported (metric name, value, standard deviation if given, dataset split, method)
- The corresponding result from Phase 5
- The reproducibility target applicable to this result
- The comparison to be performed

---

## Comparison Methodology

Result comparisons use deterministic threshold-based classification (implemented in `tools/deterministic_comparison.py`). The LLM is strictly used for narrative generation and discrepancy attribution, not for making the actual classification judgments.

### Exact Comparison
Apply when reproducibility target is Exact. Compare outputs bit-for-bit or floating-point identical. Any difference, however small, is a discrepancy.

### Numerical Comparison
Apply when reproducibility target is Numerical. For each metric:
- Compute the absolute and relative difference between reported and reproduced values
- Classify as:
  - **Match:** difference is within floating-point tolerance (e.g., < 1e-6 relative error)
  - **Close Match:** difference is small but outside floating-point tolerance (e.g., < 1% relative error) — likely due to minor implementation differences
  - **Moderate Discrepancy:** difference is between 1% and 10% relative error — warrants investigation
  - **Significant Discrepancy:** difference exceeds 10% relative error — indicates a potentially substantive difference in implementation or data

### Statistical Comparison
Apply when reproducibility target is Statistical (i.e., when no random seeds were specified and multiple runs were performed in Phase 5). For each metric:
- Compute the mean and standard deviation of the reproduced results across runs
- Assess whether the paper's reported value falls within the reproduced distribution (e.g., within 2 standard deviations of the reproduced mean)
- Classify as:
  - **Statistically Consistent:** paper's value within the reproduced distribution
  - **Borderline:** paper's value at the edge of the reproduced distribution — possible but not clearly expected
  - **Statistically Inconsistent:** paper's value falls well outside the reproduced distribution

### Qualitative Comparison
Apply when reproducibility target is Qualitative or when quantitative comparison is not possible. Assess:
- Do the reproduced results support the same directional claims? (e.g., if the paper claims method A outperforms method B, does the replication show the same ordering?)
- Do the reproduced visualizations show the same patterns described in the paper?
- Do the reproduced results support the conclusions stated in the paper's conclusion section?

---

## Discrepancy Analysis

For every result classified as anything other than Match or Statistically Consistent, perform a discrepancy analysis:

### Step 1: Identify Likely Causes
Review the audit logs from Phases 3, 4, and 5 and identify which documented assumptions, gaps, or failures could explain the discrepancy. Candidate causes include:
- Missing or inferred random seed (Phase 3)
- Preprocessing assumption that may have been wrong (Phase 4)
- Hyperparameter default that differed from the paper's actual value (Phase 5)
- Hardware differences affecting floating-point behavior (Phase 3)
- Metric ambiguity resolved differently from the paper's intent (Phase 5)
- Data version mismatch (Phase 2)

### Step 2: Quantify the Attribution
For each candidate cause, assess:
- How likely is it that this cause explains the observed discrepancy?
- If this cause were corrected (i.e., if the actual value were known), would the discrepancy be reduced?

### Step 3: Classify the Discrepancy
Based on the attribution analysis, classify each discrepancy as:

- **Explained:** the discrepancy is fully accounted for by one or more documented assumptions or gaps (e.g., a different preprocessing assumption was used, or no random seed was available)
- **Partially Explained:** some factors are identified that likely contribute, but they do not fully account for the magnitude of the discrepancy
- **Unexplained:** no documented assumption or gap can plausibly account for the discrepancy

Unexplained discrepancies are the most significant finding of the reproducibility assessment. They may indicate: an error in the paper's reported results, an undisclosed methodological step, environment-specific behavior, or a genuine implementation difference.

---

## Figure and Visualization Comparison

Many papers report results primarily through figures. For each figure described in the PKA:

- Reproduce the equivalent visualization from Phase 5 outputs
- Compare visually and, where possible, quantitatively (e.g., extract data points from the original figure using digitization if needed)
- Assess whether the reproduced figure shows the same patterns, trends, and relationships
- Note any qualitative differences (e.g., different cluster structure, different curve shape, different class separation)

---

## Claim-Level Assessment

Beyond individual metrics, assess the paper's core claims. From the PKA's Conclusions section, extract each distinct claim the paper makes about its results. For each claim, assess:

- **Supported:** the reproduced results clearly support this claim
- **Partially Supported:** the reproduced results are directionally consistent but the magnitude of the effect is different
- **Not Supported:** the reproduced results do not support this claim
- **Cannot Assess:** the relevant result could not be reproduced due to a blocking failure or missing data

This claim-level assessment is the highest-level summary of the reproducibility exercise and is the most important section of the final report.

---

## Report Generation

### Report Structure

The final reproducibility report is structured as follows:

**1. Executive Summary**
A brief, plain-language summary of the replication attempt:
- Which paper was replicated
- What data and environment were used
- Overall reproducibility assessment (high / moderate / low / failed)
- The most significant finding (positive or negative)

**2. Replication Configuration**
- Phase 1: summary of what was extracted from the paper
- Phase 2: data acquisition status (which datasets were found, which were not)
- Phase 3: environment reconstruction summary and reproducibility target
- Phase 4: preprocessing replication status and key assumptions
- Phase 5: execution status, failures, and key implementation decisions

**3. Result-by-Result Comparison**
A table for each group of related results (e.g., classification metrics, ablation study results, baseline comparisons) showing:
- Metric name
- Reported value
- Reproduced value (or distribution for statistical comparisons)
- Comparison classification (Match / Close Match / Moderate Discrepancy / Significant Discrepancy / etc.)
- Primary attributed cause of any discrepancy

**4. Figure Comparison**
Side-by-side comparison of reproduced figures with descriptions of the original figures from the paper.

**5. Discrepancy Analysis**
Detailed analysis of each non-matching result, covering likely causes and classification (explained / partially explained / unexplained).

**6. Claim-Level Assessment**
Table of all claims from the paper's conclusions with their reproducibility assessment.

**7. Known Gaps and Limitations**
- All Citation Dependency Records from Phase 1
- All unresolved failures from Phase 5
- All data that could not be sourced from Phase 2
- Any preprocessing steps that could not be faithfully replicated from Phase 4

**8. Recommendations**
Specific, actionable recommendations for:
- What the original authors could provide to make future replication easier (seeds, code, data)
- What a future replicator would need to do differently to close the remaining gaps
- Which results are most in need of further scrutiny

**9. Appendix: Full Audit Logs**
Complete logs from all phases, including all assumption records, gap records, failure records, and provenance information.

---

## Overall Reproducibility Score

Assign an overall reproducibility score based on the following criteria:

- **High Reproducibility:** All primary results reproduced within the defined target (exact, numerical, or statistical). Core claims are supported. All discrepancies are explained.
- **Moderate Reproducibility:** Most primary results reproduced within the defined target. Some unexplained discrepancies exist but do not overturn core claims. Some preprocessing or hyperparameter gaps remain.
- **Low Reproducibility:** A significant number of primary results cannot be reproduced within the defined target. Some core claims are not supported. Multiple unexplained discrepancies exist.
- **Replication Failed:** Critical blocking failures in one or more phases prevented a meaningful comparison. The paper lacks sufficient methodological detail for independent replication.

The score is accompanied by a detailed justification referencing specific findings from the report.

---

## Output

The output of this phase — and of the entire pipeline — is:

1. **Reproducibility Report (PDF and structured JSON):** the complete report as described above
2. **Result comparison table (CSV):** all reported vs. reproduced values in a machine-readable format
3. **Reproduced figures:** all visualizations generated during Phase 5, organized by the paper figure they correspond to
4. **Complete audit archive:** all logs, assumption records, code, and data manifests from all phases, packaged together for full transparency

The report is the primary deliverable of the entire reproducibility pipeline.
