from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class FigureRef(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    caption: str
    page_number: int

class TableRef(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str
    caption: str
    page_number: int
    content: Optional[str] = None

class ParsedPaper(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    pages: List[str]
    figures: List[FigureRef]
    tables: List[TableRef]
    metadata: Dict[str, Any]
