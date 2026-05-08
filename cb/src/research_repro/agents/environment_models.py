from pydantic import BaseModel, ConfigDict
from research_repro.schemas.environment_spec import DependencyRecord, HardwareGap, EnvironmentAssumption, ReproducibilityTarget
from typing import Literal

class InferredDependencies(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    dependencies: list[DependencyRecord]
    environment_assumptions: list[EnvironmentAssumption]
    python_version: str

class HardwareMapping(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    hardware_gaps: list[HardwareGap]

class ReproducibilityTargetResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    target: ReproducibilityTarget

class EnvironmentYaml(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    yaml_content: str
