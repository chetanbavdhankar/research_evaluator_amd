from typing import List, Optional
from .base import ResolutionResult
from ..models import DataAsset, FetchScript

class GenericAdapter:
    name: str = "generic"
    priority: int = 10

    def detect(self, paper_text: str) -> float:
        return 1.0  # Always applies as a fallback

    def known_archives(self) -> List[str]:
        return ["Zenodo", "Figshare", "OSF", "Dataverse", "GitHub", "HuggingFace"]

    def resolve_dataset(self, asset: DataAsset, paper_text: str) -> ResolutionResult:
        log = []
        if not asset.archive_hint:
            return ResolutionResult(status="unknown", log=["No archive hint provided."])
            
        hint = asset.archive_hint.lower()
        if "zenodo" in hint or "doi" in hint:
            log.append("Matched Zenodo/DOI pattern.")
            body = f'import httpx\nprint("Resolving DOI for {asset.name}")'
            fetch = FetchScript(language="python", body=body, requires=["httpx"])
            return ResolutionResult(status="resolved", fetch_script=fetch, log=log)
            
        if "github" in hint:
            log.append("Matched GitHub repo.")
            body = f'git clone https://github.com/placeholder/{asset.name.replace(" ", "")}'
            fetch = FetchScript(language="bash", body=body)
            return ResolutionResult(status="resolved", fetch_script=fetch, log=log)

        return ResolutionResult(status="unknown", log=["Generic adapter could not resolve."])

    def standard_pipelines(self, instrument: Optional[str]) -> List[str]:
        return []
