from typing import Protocol, List, Optional
from dataclasses import dataclass, field
from ..models import DataAsset, FetchScript

@dataclass
class ResolutionResult:
    status: str  # "resolved", "partial", "blocked", "unknown"
    fetch_script: Optional[FetchScript] = None
    log: List[str] = field(default_factory=list)

class DomainAdapter(Protocol):
    name: str
    priority: int

    def detect(self, paper_text: str) -> float:
        """Return confidence in [0, 1] that this adapter handles the paper."""

    def known_archives(self) -> List[str]:
        """Archives this adapter can resolve against."""

    def resolve_dataset(self, asset: DataAsset, paper_text: str) -> ResolutionResult:
        """Attempt to produce a download_recipe. Never raises."""

    def standard_pipelines(self, instrument: Optional[str]) -> List[str]:
        """Map 'standard reduction' phrases to concrete pipeline names."""
