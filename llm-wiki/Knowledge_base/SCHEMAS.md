# Inter-Phase Schemas

## Purpose

This document defines the structured artifacts that flow between phases. Every phase consumes and produces artifacts conforming to these schemas. The schemas are the formal contract between phases — when an agent generates output for a phase, that output must validate against the corresponding Pydantic model defined here.

The schemas in this document are reference specifications. The actual Pydantic implementations live in `src/schemas/`. When the two diverge, the Pydantic implementation is canonical and this document must be updated.

---

## Conventions

- All models are Pydantic v2 models with strict mode enabled
- Field names are `snake_case`
- All datetime fields use ISO 8601 strings
- All file paths are relative to the run directory unless explicitly absolute
- Optional fields are typed `Optional[T]` with default `None`
- Lists default to empty lists, not None
- Enums are used for closed sets of values

---

## Common Records (`schemas/common.py`)

Reusable record types referenced by multiple phase schemas.

### CitationDependency

Raised by Phase 1 when a method or dataset is referenced by citation only.

```python
class CitationDependency(BaseModel):
    item_type: Literal["method", "dataset", "preprocessing_step", "baseline"]
    item_name: str
    citation_text: str          # the citation as written in the paper
    citation_reference: str     # the entry in the references section
    location_in_paper: str      # section name and approximate position
    impact: Literal["core", "peripheral"]
    notes: Optional[str] = None
```

### AmbiguityFlag

Generic flag for any underspecified detail.

```python
class AmbiguityFlag(BaseModel):
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
```

### ExecutionFailure

Captured when generated code fails to execute as expected.

```python
class ExecutionFailure(BaseModel):
    failure_type: Literal[
        "environment",
        "data",
        "implementation",
        "convergence",
        "resource",
        "hard",
        "soft"
    ]
    phase: int                  # which phase produced this
    code_path: str              # path to the offending script
    error_message: str
    stack_trace: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None
    runtime_seconds: Optional[float] = None
    resolution_status: Literal["resolved", "unresolved", "blocking"]
    resolution_notes: Optional[str] = None
```

### HumanInterventionFlag

Raised when human input is required.

```python
class HumanInterventionFlag(BaseModel):
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
    blocking: bool              # if True, pipeline cannot continue without resolution
```

### ProvenanceRecord

Tracks the origin of any acquired artifact.

```python
class ProvenanceRecord(BaseModel):
    source_url: Optional[str] = None
    access_method: str          # e.g., "huggingface_datasets", "direct_download", "kaggle_api"
    download_timestamp: datetime
    file_hash_sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    version_identifier: Optional[str] = None
```

---

## Phase 1 Output: PaperKnowledgeArtifact (`schemas/paper_knowledge.py`)

```python
class PaperMetadata(BaseModel):
    title: str
    authors: list[str]
    venue: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    input_source: str           # original URL or file path provided

class PaperSummary(BaseModel):
    abstract: str
    research_question: str
    domain: str                 # e.g., "computer vision", "macroeconomics", "molecular biology"
    claimed_contributions: list[str]

class DatasetDescription(BaseModel):
    name: str
    description: str
    source_type: Literal["public_specified", "public_partial", "author_provided", "proprietary", "custom_generated", "unspecified"]
    source_links: list[str] = []
    time_range: Optional[str] = None
    size_description: Optional[str] = None
    format: Optional[str] = None
    splits: Optional[str] = None       # description of train/val/test split as given
    notes: Optional[str] = None

class PreprocessingStep(BaseModel):
    step_id: str                # e.g., "step_01"
    operation_type: str
    description: str
    inputs: list[str]
    parameters: dict[str, Any] = {}
    output_description: str
    paper_quote: str            # the sentence(s) in the paper this is derived from
    location_in_paper: str
    order_index: int
    ambiguities: list[AmbiguityFlag] = []

class MethodSpecification(BaseModel):
    method_id: str
    name: str
    method_type: str            # e.g., "supervised_classifier", "statistical_test", "clustering"
    description: str
    hyperparameters: dict[str, Any] = {}
    training_procedure: Optional[str] = None
    evaluation_metric: Optional[str] = None
    evaluation_split: Optional[str] = None
    paper_quote: str
    location_in_paper: str
    depends_on: list[str] = []   # method_ids of prerequisite methods
    citation_dependency: Optional[CitationDependency] = None

class ResultRecord(BaseModel):
    result_id: str
    description: str
    metric_name: str
    reported_value: float
    reported_uncertainty: Optional[float] = None
    method_id: str              # which MethodSpecification produced it
    dataset_split: Optional[str] = None
    location_in_paper: str
    figure_or_table: Optional[str] = None

class PaperKnowledgeArtifact(BaseModel):
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
```

---

## Phase 2 Output: DataManifest (`schemas/data_manifest.py`)

```python
class DataAcquisitionRecord(BaseModel):
    dataset_name: str
    category: Literal["A_public_specified", "B_public_partial", "C_author_provided", "D_proprietary", "E_custom_generated", "F_unspecified"]
    status: Literal["acquired", "partial", "blocked", "skipped"]
    local_path: Optional[str] = None    # relative to run directory
    provenance: Optional[ProvenanceRecord] = None
    schema_validation: Optional[dict[str, Any]] = None
    size_validation: Optional[dict[str, Any]] = None
    statistical_validation: Optional[dict[str, Any]] = None
    discrepancies: list[str] = []
    intervention_flags: list[HumanInterventionFlag] = []

class DataManifest(BaseModel):
    paper_artifact_path: str    # path to PaperKnowledgeArtifact JSON
    acquisitions: list[DataAcquisitionRecord]
    overall_status: Literal["all_acquired", "partial", "blocked"]
    intervention_flags: list[HumanInterventionFlag] = []
    readiness_summary: str
```

---

## Phase 3 Output: EnvironmentSpec (`schemas/environment_spec.py`)

```python
class DependencyRecord(BaseModel):
    name: str
    version: Optional[str] = None
    confidence: Literal["confirmed", "inferred", "unknown"]
    inference_reasoning: Optional[str] = None

class HardwareGap(BaseModel):
    paper_hardware: str
    available_hardware: str
    impact_assessment: str

class EnvironmentAssumption(BaseModel):
    description: str
    reasoning: str
    confidence: Literal["high", "medium", "low"]
    risk_if_wrong: str

class ReproducibilityTarget(BaseModel):
    target_type: Literal["exact", "numerical", "statistical", "qualitative"]
    justification: str
    numerical_tolerance: Optional[float] = None  # only for "numerical" target

class EnvironmentSpec(BaseModel):
    language: str
    language_version: Optional[str] = None
    dependencies: list[DependencyRecord]
    dependency_conflicts: list[str] = []
    hardware_gaps: list[HardwareGap] = []
    environment_assumptions: list[EnvironmentAssumption] = []
    environment_yml_path: str           # generated environment.yml file
    requirements_txt_path: Optional[str] = None
    conda_env_name: str
    provisioning_status: Literal["provisioned", "failed"]
    provisioning_errors: list[str] = []
    reproducibility_target: ReproducibilityTarget
    random_seeds: dict[str, int] = {}    # named seeds extracted from paper
```

---

## Phase 4 Output: ProcessedDatasetArtifact (`schemas/processed_dataset.py`)

```python
class PreprocessingExecutionRecord(BaseModel):
    step_id: str                # matches PreprocessingStep.step_id from Phase 1
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
    dataset_name: str
    train_path: Optional[str] = None
    validation_path: Optional[str] = None
    test_path: Optional[str] = None
    full_path: Optional[str] = None      # if no split was performed
    schema: dict[str, str]                # column name -> dtype
    sample_count: int

class ProcessedDatasetArtifact(BaseModel):
    paper_artifact_path: str
    data_manifest_path: str
    environment_spec_path: str
    processed_datasets: list[ProcessedDataset]
    preprocessing_execution: list[PreprocessingExecutionRecord]
    pipeline_code_path: str             # the assembled preprocessing script
    replicability_assessment: Literal["fully_faithful", "partially_faithful", "substantially_deviated"]
    replicability_notes: str
    intervention_flags: list[HumanInterventionFlag] = []
```

---

## Phase 5 Output: AnalysisResultsPackage (`schemas/analysis_results.py`)

```python
class MethodExecutionRecord(BaseModel):
    method_id: str              # matches MethodSpecification.method_id from Phase 1
    code_path: str
    executed: bool
    seed_runs: list[dict[str, Any]] = []   # one entry per seed if multi-run
    primary_outputs: dict[str, Any] = {}    # metric_name -> value(s)
    intermediate_outputs: dict[str, str] = {}  # name -> path to artifact
    figures: list[str] = []              # paths to generated figures
    hyperparameters_used: dict[str, Any] = {}
    hyperparameter_defaults: list[dict[str, Any]] = []  # which were defaulted
    metric_ambiguities: list[AmbiguityFlag] = []
    failures: list[ExecutionFailure] = []
    execution_log_path: str
    runtime_seconds: float
    resource_usage: dict[str, Any] = {}     # peak memory, GPU utilization, etc.

class SensitivityAnalysisResult(BaseModel):
    hyperparameter: str
    values_tested: list[Any]
    metric_values: list[float]
    sensitivity_assessment: Literal["low", "medium", "high"]

class AnalysisResultsPackage(BaseModel):
    paper_artifact_path: str
    processed_dataset_path: str
    environment_spec_path: str
    method_executions: list[MethodExecutionRecord]
    sensitivity_analyses: list[SensitivityAnalysisResult] = []
    overall_status: Literal["complete", "partial", "blocked"]
    intervention_flags: list[HumanInterventionFlag] = []
```

---

## Phase 6 Output: ReproducibilityReport (`schemas/reproducibility_report.py`)

```python
class ResultComparison(BaseModel):
    result_id: str              # matches ResultRecord.result_id from Phase 1
    metric_name: str
    reported_value: float
    reproduced_value: Optional[float] = None
    reproduced_distribution: Optional[dict[str, float]] = None  # mean, std, min, max
    classification: Literal[
        "match",
        "close_match",
        "moderate_discrepancy",
        "significant_discrepancy",
        "statistically_consistent",
        "borderline",
        "statistically_inconsistent",
        "qualitative_match",
        "qualitative_mismatch",
        "not_reproduced"
    ]
    absolute_difference: Optional[float] = None
    relative_difference: Optional[float] = None

class DiscrepancyAttribution(BaseModel):
    result_id: str
    candidate_causes: list[str]
    most_likely_cause: Optional[str] = None
    classification: Literal["explained", "partially_explained", "unexplained"]
    notes: str

class ClaimAssessment(BaseModel):
    claim_text: str
    supporting_results: list[str]   # result_ids
    assessment: Literal["supported", "partially_supported", "not_supported", "cannot_assess"]
    rationale: str

class ReproducibilityReport(BaseModel):
    paper_artifact_path: str
    all_phase_outputs: dict[str, str]   # phase name -> artifact path
    
    executive_summary: str
    overall_score: Literal["high", "moderate", "low", "failed"]
    overall_score_justification: str
    
    result_comparisons: list[ResultComparison]
    discrepancy_attributions: list[DiscrepancyAttribution]
    claim_assessments: list[ClaimAssessment]
    
    figure_comparisons: list[dict[str, str]] = []   # {paper_figure_id, reproduced_figure_path, notes}
    
    known_gaps: list[str]
    recommendations: list[str]
    
    pdf_report_path: str
    json_report_path: str
```

---

## Pipeline State (`schemas/pipeline_state.py`)

The single state object passed through the LangGraph state graph.

```python
class PhaseStatus(BaseModel):
    phase_number: int
    phase_name: str
    status: Literal["pending", "in_progress", "complete", "partial", "blocked", "failed"]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_path: Optional[str] = None
    flags_raised: list[str] = []

class PipelineState(BaseModel):
    run_id: str
    run_directory: str
    paper_input: str
    config_path: str
    mode: Literal["auto", "interactive"]
    
    phase_statuses: list[PhaseStatus]
    
    paper_knowledge_artifact: Optional[str] = None      # path
    data_manifest: Optional[str] = None
    environment_spec: Optional[str] = None
    processed_dataset_artifact: Optional[str] = None
    analysis_results_package: Optional[str] = None
    reproducibility_report: Optional[str] = None
    
    overall_status: Literal["initialized", "running", "paused_for_input", "complete", "terminated"]
    last_updated: datetime
```

---

## Schema Validation Protocol

Every phase executor must:

1. **On input:** Load the previous phase's JSON output, instantiate it via `model_validate_json()`. If validation fails, the phase aborts with a clear error pointing to the offending field.

2. **On output:** Construct the output as a Pydantic model, then call `model_dump_json(indent=2)` to serialize. The orchestrator then validates the written file by reloading it. Any deserialization failure is treated as a phase failure.

3. **For agent-generated content:** When an agent produces a sub-structure (e.g., a `PreprocessingStep`), the agent is given the schema as part of its prompt and asked to return JSON. The phase executor validates the agent's output against the schema and retries (up to 3 times) on validation failure.

---

## Schema Evolution

When a schema needs to change:

1. The change is made first in `src/schemas/` (the canonical source)
2. This document is updated to match
3. A migration note is added to the schema's docstring with the date and rationale
4. If the change is backward-incompatible, run directories from before the change cannot be resumed; they are flagged as legacy

For the hackathon, schemas are expected to stabilize quickly and not require migrations. Any change during the hackathon should be small and made simultaneously across all affected files.
