from pydantic import BaseModel, ConfigDict
from typing import Literal

class DatasetClassification(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    category: Literal["A_public_specified", "B_public_partial", "C_author_provided", "D_proprietary", "E_custom_generated", "F_unspecified"]
    reasoning: str
    search_query_if_needed: str = ""

class DownloadScript(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    python_code: str
    required_packages: list[str]
