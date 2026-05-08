# Source: SCHEMAS.md §Phase 2 Output
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional, Any
from research_repro.schemas.common import ProvenanceRecord, HumanInterventionFlag

class DataAcquisitionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    dataset_name: str
    category: Literal["A_public_specified", "B_public_partial", "C_author_provided", "D_proprietary", "E_custom_generated", "F_unspecified"]
    status: Literal["acquired", "partial", "blocked", "skipped"]
    local_path: Optional[str] = None
    provenance: Optional[ProvenanceRecord] = None
    schema_validation: Optional[dict[str, Any]] = None
    size_validation: Optional[dict[str, Any]] = None
    statistical_validation: Optional[dict[str, Any]] = None
    discrepancies: list[str] = []
    intervention_flags: list[HumanInterventionFlag] = []

class DataManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    paper_artifact_path: str
    acquisitions: list[DataAcquisitionRecord]
    overall_status: Literal["all_acquired", "partial", "blocked"]
    intervention_flags: list[HumanInterventionFlag] = []
    readiness_summary: str
