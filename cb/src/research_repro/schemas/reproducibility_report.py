# Source: SCHEMAS.md §Phase 6 Output
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional

class ResultComparison(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    result_id: str
    metric_name: str
    reported_value: float
    reproduced_value: Optional[float] = None
    reproduced_distribution: Optional[dict[str, float]] = None
    classification: Literal[
        "match",
        "close_match",
        "moderate_discrepancy",
        "significant_discrepancy",
        "statistically_consistent",
        "borderline",
        "statistically_inconsistent",
        "qualitative_match",
        "qualitative_mismatch",
        "not_reproduced"
    ]
    absolute_difference: Optional[float] = None
    relative_difference: Optional[float] = None

class DiscrepancyAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    result_id: str
    candidate_causes: list[str]
    most_likely_cause: Optional[str] = None
    classification: Literal["explained", "partially_explained", "unexplained"]
    notes: str

class ClaimAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    claim_text: str
    supporting_results: list[str]
    assessment: Literal["supported", "partially_supported", "not_supported", "cannot_assess"]
    rationale: str

class ReproducibilityReport(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    paper_artifact_path: str
    all_phase_outputs: dict[str, str]
    
    executive_summary: str
    overall_score: Literal["high", "moderate", "low", "failed"]
    overall_score_justification: str
    
    result_comparisons: list[ResultComparison]
    discrepancy_attributions: list[DiscrepancyAttribution]
    claim_assessments: list[ClaimAssessment]
    
    figure_comparisons: list[dict[str, str]] = []
    
    known_gaps: list[str]
    recommendations: list[str]
    
    pdf_report_path: str
    json_report_path: str
