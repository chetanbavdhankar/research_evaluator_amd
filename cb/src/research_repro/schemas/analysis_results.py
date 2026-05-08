# Source: SCHEMAS.md §Phase 5 Output
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional, Any
from research_repro.schemas.common import AmbiguityFlag, ExecutionFailure, HumanInterventionFlag

class MethodExecutionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    method_id: str
    code_path: str
    executed: bool
    seed_runs: list[dict[str, Any]] = []
    primary_outputs: dict[str, Any] = {}
    intermediate_outputs: dict[str, str] = {}
    figures: list[str] = []
    hyperparameters_used: dict[str, Any] = {}
    hyperparameter_defaults: list[dict[str, Any]] = []
    metric_ambiguities: list[AmbiguityFlag] = []
    failures: list[ExecutionFailure] = []
    execution_log_path: str
    runtime_seconds: float
    resource_usage: dict[str, Any] = {}

class SensitivityAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    hyperparameter: str
    values_tested: list[Any]
    metric_values: list[float]
    sensitivity_assessment: Literal["low", "medium", "high"]

class AnalysisResultsPackage(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    paper_artifact_path: str
    processed_dataset_path: str
    environment_spec_path: str
    method_executions: list[MethodExecutionRecord]
    sensitivity_analyses: list[SensitivityAnalysisResult] = []
    overall_status: Literal["complete", "partial", "blocked"]
    intervention_flags: list[HumanInterventionFlag] = []
