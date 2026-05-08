from pydantic import BaseModel, ConfigDict

class AnalysisScript(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    python_code: str
    hyperparameter_defaults_assumed: dict[str, str]
    metric_ambiguities_resolved: list[str]
