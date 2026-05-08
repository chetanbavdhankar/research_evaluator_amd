from typing import List, Optional
from .base import ResolutionResult
from ..models import DataAsset, FetchScript

class AstroAdapter:
    name: str = "astro"
    priority: int = 100

    def detect(self, paper_text: str) -> float:
        keywords = ["telescope", "spectroscopy", "galaxy", "redshift", "keck", "hst", "alma"]
        matches = sum(1 for kw in keywords if kw.lower() in paper_text.lower())
        return min(1.0, matches / 3.0)

    def known_archives(self) -> List[str]:
        return ["KOA", "MAST", "ESO", "IRSA", "VizieR", "ALMA", "HEASARC", "SDSS CAS"]

    def resolve_dataset(self, asset: DataAsset, paper_text: str) -> ResolutionResult:
        log = []
        if asset.kind not in ["dataset", "catalog", "raw_obs"]:
            return ResolutionResult(status="unknown", log=["Astro adapter ignores non-data assets."])

        # Stub implementation mapping identified names to standard fetching recipes.
        # In a full M3 implementation, this uses `astroquery` or pyvo to resolve canonical IDs.
        
        script_body = f'# TODO: Query {asset.archive_hint or "UnknownArchive"} for asset ID {asset.name}\nprint("Fetching {asset.name}")'
        
        if "keck" in asset.name.lower() or asset.archive_hint == "KOA":
            log.append("Identified as Keck/KOA target.")
            script_body = f"from astroquery.koa import Koa\n# Koa.query_target('{asset.name}')"
        elif "hst" in asset.name.lower() or asset.archive_hint == "MAST":
            log.append("Identified as HST/MAST target.")
            script_body = f"from astroquery.mast import Observations\n# Observations.query_criteria(target_name='{asset.name}')"
        else:
            log.append("No specific astro-archive matched. Falling back to generic manual resolution.")
            return ResolutionResult(status="unknown", log=log)

        fetch = FetchScript(
            language="python",
            body=script_body,
            requires=["astroquery"]
        )
        return ResolutionResult(status="resolved", fetch_script=fetch, log=log)

    def standard_pipelines(self, instrument: Optional[str]) -> List[str]:
        if not instrument:
            return []
        instrument = instrument.lower()
        if "lris" in instrument: return ["PypeIt", "LPipe"]
        if "kcwi" in instrument: return ["KCWIDRP"]
        if "acs" in instrument or "wfc3" in instrument: return ["drizzlepac"]
        return []
