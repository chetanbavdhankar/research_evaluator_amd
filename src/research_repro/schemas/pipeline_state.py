# Source: SCHEMAS.md §Pipeline State
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional
from datetime import datetime

class PhaseStatus(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    phase_number: int
    phase_name: str
    status: Literal["pending", "in_progress", "complete", "partial", "blocked", "failed"]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_path: Optional[str] = None
    flags_raised: list[str] = []

class PipelineState(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    run_id: str
    run_directory: str
    paper_input: str
    config_path: str
    mode: Literal["auto", "interactive"]
    
    phase_statuses: list[PhaseStatus]
    
    paper_knowledge_artifact: Optional[str] = None
    data_manifest: Optional[str] = None
    environment_spec: Optional[str] = None
    processed_dataset_artifact: Optional[str] = None
    analysis_results_package: Optional[str] = None
    reproducibility_report: Optional[str] = None
    
    overall_status: Literal["initialized", "running", "paused_for_input", "complete", "terminated"]
    last_updated: datetime
