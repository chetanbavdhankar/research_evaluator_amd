# Source: SCHEMAS.md §Common Records
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional
from datetime import datetime

class VerificationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    checks_run: list[str]
    passed: bool
    attempt_count: int
    notes: Optional[str] = None

class CitationDependency(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    item_type: Literal["method", "dataset", "preprocessing_step", "baseline"]
    item_name: str
    citation_text: str
    citation_reference: str
    location_in_paper: str
    impact: Literal["core", "peripheral"]
    notes: Optional[str] = None

class AmbiguityFlag(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    flag_type: Literal[
        "data_ambiguity",
        "preprocessing_ambiguity",
        "hyperparameter_gap",
        "result_traceability_gap",
        "metric_ambiguity",
        "feature_engineering_assumption",
        "stochastic_assumption",
        "pipeline_order_assumption",
        "version_ambiguity",
        "size_mismatch",
        "data_identification_ambiguity"
    ]
    description: str
    location_in_paper: Optional[str] = None
    assumption_made: Optional[str] = None
    sensitivity: Literal["low", "medium", "high"]

class ExecutionFailure(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    failure_type: Literal[
        "environment",
        "data",
        "implementation",
        "convergence",
        "resource",
        "hard",
        "soft"
    ]
    phase: int
    code_path: str
    error_message: str
    stack_trace: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    runtime_seconds: Optional[float] = None
    resolution_status: Literal["resolved", "unresolved", "blocking"]
    resolution_notes: Optional[str] = None

class HumanInterventionFlag(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    flag_type: Literal[
        "restricted_data",
        "custom_data_generation",
        "data_access_failure",
        "data_source_unknown",
        "missing_split_seed",
        "missing_random_seed",
        "blocking_environment_failure",
        "blocking_data_failure",
        "blocking_implementation_failure",
        "convergence_failure",
        "resource_constraint_failure"
    ]
    phase: int
    description: str
    suggested_action: str
    blocking: bool

class ProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    source_url: Optional[str] = None
    access_method: str
    download_timestamp: datetime
    file_hash_sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    version_identifier: Optional[str] = None
