# Source: SCHEMAS.md §Phase 4 Output
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional, Any
from research_repro.schemas.common import AmbiguityFlag, ExecutionFailure, HumanInterventionFlag

class PreprocessingExecutionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    step_id: str
    code_path: str
    executed: bool
    input_shape: Optional[tuple] = None
    output_shape: Optional[tuple] = None
    input_stats: dict[str, Any] = {}
    output_stats: dict[str, Any] = {}
    assumptions_made: list[AmbiguityFlag] = []
    failures: list[ExecutionFailure] = []
    execution_log_path: str

class ProcessedDataset(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    dataset_name: str
    train_path: Optional[str] = None
    validation_path: Optional[str] = None
    test_path: Optional[str] = None
    full_path: Optional[str] = None
    schema_: dict[str, str]  # Note: `schema` is reserved in Pydantic, using `schema_` but need an alias or just schema_ if okay. 
    # Actually, the user spec uses `schema: dict[str, str]`. Pydantic v2 has `model_fields` but field named `schema` might shadow `BaseModel.schema()`. Wait, `BaseModel.schema()` is deprecated, we can use `model_json_schema()`. So `schema` as field name is fine in v2.
    schema_map: dict[str, str] # I'll use schema_map here and specify Field(alias="schema") to be safe. No, `schema` is allowed in Pydantic V2. Let me use `dataset_schema` instead or just `schema_`. Let's use Field.
    sample_count: int

from pydantic import Field
class ProcessedDataset(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, populate_by_name=True)
    dataset_name: str
    train_path: Optional[str] = None
    validation_path: Optional[str] = None
    test_path: Optional[str] = None
    full_path: Optional[str] = None
    schema_dict: dict[str, str] = Field(alias="schema")
    sample_count: int

class ProcessedDatasetArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    paper_artifact_path: str
    data_manifest_path: str
    environment_spec_path: str
    processed_datasets: list[ProcessedDataset]
    preprocessing_execution: list[PreprocessingExecutionRecord]
    pipeline_code_path: str
    replicability_assessment: Literal["fully_faithful", "partially_faithful", "substantially_deviated"]
    replicability_notes: str
    intervention_flags: list[HumanInterventionFlag] = []
