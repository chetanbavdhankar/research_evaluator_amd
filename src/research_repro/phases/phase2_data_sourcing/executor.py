import os
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel
from research_repro.config import AppConfig
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.data_manifest import DataManifest, DataAcquisitionRecord
from research_repro.schemas.common import HumanInterventionFlag
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.sourcer import SourcingAgent
from research_repro.logging_setup import get_phase_logger
from research_repro.phases.phase1_paper_comprehension.executor import PhaseResult

def run(pka_path: str, run_dir: Path, config: AppConfig) -> PhaseResult:
    logger = get_phase_logger(str(run_dir), 2, "executor")
    logger.info(f"Starting Phase 2 for {pka_path}")
    
    with open(pka_path, "r", encoding="utf-8") as f:
        pka = PaperKnowledgeArtifact.model_validate_json(f.read())
        
    llm_client = LLMClient(config)
    sourcer = SourcingAgent(llm_client)
    
    data_dir = run_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    acquisitions = []
    overall_flags = []
    
    for ds in pka.datasets:
        logger.info(f"Processing dataset: {ds.name}")
        
        classification = sourcer.classify_dataset(ds)
        logger.info(f"Classified {ds.name} as {classification.category}")
        
        record = DataAcquisitionRecord(
            dataset_name=ds.name,
            category=classification.category,
            status="skipped"
        )
        
        if classification.category in ["A_public_specified", "B_public_partial", "C_author_provided"]:
            logger.info(f"Generating download script for {ds.name}")
            script = sourcer.generate_download_script(ds)
            
            dest_dir = data_dir / ds.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            script_path = dest_dir / "download.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script.python_code)
                
            env = os.environ.copy()
            env["DATA_DEST_DIR"] = str(dest_dir.resolve())
            
            # Subprocess execution
            try:
                # We would normally want to ensure required_packages are installed
                # For M3, we assume basic packages or run `pip install` first.
                # Let's run a simple `uv pip install` if there are requirements.
                if script.required_packages:
                    subprocess.run(["uv", "pip", "install"] + script.required_packages, check=True, capture_output=True)
                    
                result = subprocess.run(
                    ["python", str(script_path)],
                    env=env,
                    cwd=str(dest_dir),
                    capture_output=True,
                    text=True,
                    timeout=config.execution.subprocess_timeout_seconds
                )
                
                if result.returncode == 0:
                    record.status = "acquired"
                    record.local_path = str(dest_dir.relative_to(run_dir))
                else:
                    record.status = "blocked"
                    record.discrepancies.append(f"Script failed: {result.stderr}")
                    flag = HumanInterventionFlag(
                        flag_type="data_access_failure",
                        phase=2,
                        description=f"Failed to download {ds.name}. Stderr: {result.stderr[:200]}",
                        suggested_action="Manually download the dataset",
                        blocking=True
                    )
                    record.intervention_flags.append(flag)
                    overall_flags.append(flag)
            except Exception as e:
                record.status = "blocked"
                record.discrepancies.append(f"Execution error: {e}")
                flag = HumanInterventionFlag(
                    flag_type="data_access_failure",
                    phase=2,
                    description=f"Error executing download script: {e}",
                    suggested_action="Check script or manually download",
                    blocking=True
                )
                record.intervention_flags.append(flag)
                overall_flags.append(flag)
        else:
            # D, E, F require manual intervention
            flag_type = "data_source_unknown"
            if classification.category == "D_proprietary":
                flag_type = "restricted_data"
            elif classification.category == "E_custom_generated":
                flag_type = "custom_data_generation"
                
            flag = HumanInterventionFlag(
                flag_type=flag_type,
                phase=2,
                description=f"Dataset {ds.name} is {classification.category}.",
                suggested_action="Provide data manually.",
                blocking=True
            )
            record.status = "blocked"
            record.intervention_flags.append(flag)
            overall_flags.append(flag)
            
        acquisitions.append(record)
        
    overall_status = "all_acquired"
    if any(a.status == "blocked" for a in acquisitions):
        overall_status = "blocked"
    elif any(a.status == "partial" for a in acquisitions):
        overall_status = "partial"
        
    manifest = DataManifest(
        paper_artifact_path=pka_path,
        acquisitions=acquisitions,
        overall_status=overall_status,
        intervention_flags=overall_flags,
        readiness_summary=f"{overall_status.replace('_', ' ').title()}"
    )
    
    output_path = run_dir / "data_manifest.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))
        
    return PhaseResult(status="complete" if overall_status == "all_acquired" else overall_status, 
                       artifact_path=str(output_path.resolve()), 
                       flags_raised=[f.description for f in overall_flags])
