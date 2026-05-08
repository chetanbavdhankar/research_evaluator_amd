from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional

class ValidationNarrative(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    executive_summary: str
    overall_score: Literal["high", "moderate", "low", "failed"]
    overall_score_justification: str
    recommendations: list[str]

class ClaimAssessmentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    assessment: Literal["supported", "partially_supported", "not_supported", "cannot_assess"]
    rationale: str

class DiscrepancyExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    candidate_causes: list[str]
    most_likely_cause: Optional[str]
    classification: Literal["explained", "partially_explained", "unexplained"]
    notes: str
