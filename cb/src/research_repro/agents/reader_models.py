from pydantic import BaseModel, ConfigDict
from research_repro.schemas.paper_knowledge import (
    DatasetDescription, PreprocessingStep, MethodSpecification, 
    ResultRecord
)
from research_repro.schemas.common import CitationDependency, AmbiguityFlag

class DatasetDescriptionsList(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[DatasetDescription]

class PreprocessingStepList(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[PreprocessingStep]

class MethodSpecificationList(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[MethodSpecification]

class ResultRecordList(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[ResultRecord]

class StringList(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[str]

class CitationDependencyList(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[CitationDependency]

class AmbiguityFlagList(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[AmbiguityFlag]

class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    assessment: str
