# Source: SCHEMAS.md §Phase 3 Output
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional

class DependencyRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    name: str
    version: Optional[str] = None
    confidence: Literal["confirmed", "inferred", "unknown"]
    inference_reasoning: Optional[str] = None

class HardwareGap(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    paper_hardware: str
    available_hardware: str
    impact_assessment: str

class EnvironmentAssumption(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    description: str
    reasoning: str
    confidence: Literal["high", "medium", "low"]
    risk_if_wrong: str

class ReproducibilityTarget(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    target_type: Literal["exact", "numerical", "statistical", "qualitative"]
    justification: str
    numerical_tolerance: Optional[float] = None

class EnvironmentSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    language: str
    language_version: Optional[str] = None
    dependencies: list[DependencyRecord]
    dependency_conflicts: list[str] = []
    hardware_gaps: list[HardwareGap] = []
    environment_assumptions: list[EnvironmentAssumption] = []
    environment_yml_path: str
    requirements_txt_path: Optional[str] = None
    conda_env_name: str
    provisioning_status: Literal["provisioned", "failed"]
    provisioning_errors: list[str] = []
    reproducibility_target: ReproducibilityTarget
    random_seeds: dict[str, int] = {}
