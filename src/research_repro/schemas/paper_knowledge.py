# Source: SCHEMAS.md §Phase 1 Output
from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional, Any
from research_repro.schemas.common import CitationDependency, AmbiguityFlag

class PaperMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    title: str
    authors: list[str]
    venue: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    input_source: str

class PaperSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    abstract: str
    research_question: str
    domain: str
    claimed_contributions: list[str]

class DatasetDescription(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    name: str
    description: str
    source_type: Literal["public_specified", "public_partial", "author_provided", "proprietary", "custom_generated", "unspecified"]
    source_links: list[str] = []
    time_range: Optional[str] = None
    size_description: Optional[str] = None
    format: Optional[str] = None
    splits: Optional[str] = None
    notes: Optional[str] = None

class PreprocessingStep(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    step_id: str
    operation_type: str
    description: str
    inputs: list[str]
    parameters: dict[str, Any] = {}
    output_description: str
    paper_quote: str
    location_in_paper: str
    order_index: int
    ambiguities: list[AmbiguityFlag] = []

class MethodSpecification(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    method_id: str
    name: str
    method_type: str
    description: str
    hyperparameters: dict[str, Any] = {}
    training_procedure: Optional[str] = None
    evaluation_metric: Optional[str] = None
    evaluation_split: Optional[str] = None
    paper_quote: str
    location_in_paper: str
    depends_on: list[str] = []
    citation_dependency: Optional[CitationDependency] = None

class ResultRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    result_id: str
    description: str
    metric_name: str
    reported_value: float
    reported_uncertainty: Optional[float] = None
    method_id: str
    dataset_split: Optional[str] = None
    location_in_paper: str
    figure_or_table: Optional[str] = None

class PaperKnowledgeArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    metadata: PaperMetadata
    summary: PaperSummary
    datasets: list[DatasetDescription]
    preprocessing_pipeline: list[PreprocessingStep]
    methodology: list[MethodSpecification]
    results: list[ResultRecord]
    conclusions: list[str]
    citation_dependencies: list[CitationDependency] = []
    ambiguity_flags: list[AmbiguityFlag] = []
    reproducibility_risk_assessment: str
