from pydantic import BaseModel, ConfigDict

class PreprocessingScript(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    python_code: str
    assumptions_made: list[str]
