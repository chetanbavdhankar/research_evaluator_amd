from pydantic import BaseModel, Field
from typing import Literal, Dict, List, Optional
from datetime import datetime

class AccessSpec(BaseModel):
    kind: Literal["public_direct", "public_registration", "gated", "unknown"]
    notes: str = ""
    proprietary_until: Optional[datetime] = None

class FetchScript(BaseModel):
    language: Literal["python", "bash"]
    body: str
    requires: List[str] = []
    estimated_volume_mb: Optional[int] = None

class DataAsset(BaseModel):
    id: str
    name: str
    kind: Literal["dataset", "catalog", "raw_obs", "reduced", "code", "model"]
    cited_in: List[str]
    archive_hint: Optional[str] = None
    identifiers: Dict[str, str]
    access: AccessSpec
    download_recipe: Optional[FetchScript] = None
    resolution_log: List[str] = []

class ParameterSpec(BaseModel):
    name: str
    value: str | float | int | bool | None = None
    underspecified: bool = False
    paper_quote: Optional[str] = None

class MethodStep(BaseModel):
    order: int
    name: str
    inputs: List[str]
    outputs: List[str]
    parameters: List[ParameterSpec]
    software_used: List[str]
    gap_flags: List[str]

class Software(BaseModel):
    id: str
    name: str
    version: Optional[str] = None
    source: Literal["paper_explicit", "adapter_inferred", "standard_default"]

class ComputeFootprint(BaseModel):
    cpu_hours: Optional[float] = None
    gpu_hours: Optional[float] = None
    storage_gb: Optional[float] = None
    estimator_confidence: Literal["measured", "estimated", "guessed"]
    rationale: str
