from pathlib import Path
from pydantic import BaseModel
import json
import logging
from research_repro.config import AppConfig
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.pipeline_state import PhaseStatus
from research_repro.tools.input_router import ingest_paper
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.reader import ReaderAgent
from research_repro.logging_setup import get_phase_logger

class PhaseResult(BaseModel):
    status: str
    artifact_path: str
    flags_raised: list[str]

def run(input_path: str, run_dir: Path, config: AppConfig) -> PhaseResult:
    logger = get_phase_logger(str(run_dir), 1, "executor")
    logger.info(f"Starting Phase 1 for {input_path}")
    
    try:
        parsed_paper = ingest_paper(input_path)
    except Exception as e:
        logger.error(f"Failed to ingest paper: {e}")
        return PhaseResult(status="blocked", artifact_path="", flags_raised=["Ingestion failed"])
        
    llm_client = LLMClient(config)
    reader = ReaderAgent(llm_client)
    
    try:
        metadata = reader.extract_metadata(parsed_paper)
        # Ensure we set input_source and arxiv_id from parsed metadata if available
        metadata.input_source = parsed_paper.metadata.get("input_source", input_path)
        metadata.arxiv_id = parsed_paper.metadata.get("arxiv_id", None)
        
        summary = reader.extract_summary(parsed_paper)
        datasets = reader.extract_datasets(parsed_paper)
        preprocessing = reader.extract_preprocessing_pipeline(parsed_paper)
        methodology = reader.extract_methodology(parsed_paper)
        results = reader.extract_results(parsed_paper)
        conclusions = reader.extract_conclusions(parsed_paper)
        
        citation_deps = reader.detect_citation_dependencies(parsed_paper, methodology)
        ambiguities = reader.detect_ambiguity_flags(parsed_paper)
        
        partial_pka = {
            "metadata": metadata.model_dump(),
            "summary": summary.model_dump(),
            "datasets": [d.model_dump() for d in datasets],
            "preprocessing_pipeline": [p.model_dump() for p in preprocessing],
            "methodology": [m.model_dump() for m in methodology],
            "results": [r.model_dump() for r in results],
            "conclusions": conclusions,
            "citation_dependencies": [c.model_dump() for c in citation_deps],
            "ambiguity_flags": [a.model_dump() for a in ambiguities],
        }
        
        risk = reader.assess_reproducibility_risk(partial_pka)
        
        artifact = PaperKnowledgeArtifact(
            metadata=metadata,
            summary=summary,
            datasets=datasets,
            preprocessing_pipeline=preprocessing,
            methodology=methodology,
            results=results,
            conclusions=conclusions,
            citation_dependencies=citation_deps,
            ambiguity_flags=ambiguities,
            reproducibility_risk_assessment=risk
        )
        
        output_path = run_dir / "phase1_output.json"
        tmp_path = output_path.with_suffix('.tmp')
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(artifact.model_dump_json(indent=2))
        tmp_path.replace(output_path)
        
        return PhaseResult(status="complete", artifact_path=str(output_path.resolve()), flags_raised=[])
        
    except Exception as e:
        logger.error(f"Phase 1 execution failed: {e}")
        return PhaseResult(status="blocked", artifact_path="", flags_raised=[str(e)])
