import os
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel
from research_repro.config import AppConfig
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.data_manifest import DataManifest
from research_repro.schemas.processed_dataset import ProcessedDatasetArtifact, PreprocessingExecutionRecord as ProcessingStepRecord
from research_repro.schemas.environment_spec import EnvironmentSpec
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.data_processor import DataProcessorAgent
from research_repro.logging_setup import get_phase_logger
from research_repro.phases.phase1_paper_comprehension.executor import PhaseResult

def run(pka_path: str, data_manifest_path: str, env_spec_path: str, run_dir: Path, config: AppConfig) -> PhaseResult:
    logger = get_phase_logger(str(run_dir), 4, "executor")
    logger.info(f"Starting Phase 4 for {pka_path}")
    
    with open(pka_path, "r", encoding="utf-8") as f:
        pka = PaperKnowledgeArtifact.model_validate_json(f.read())
        
    with open(data_manifest_path, "r", encoding="utf-8") as f:
        manifest = DataManifest.model_validate_json(f.read())
        
    with open(env_spec_path, "r", encoding="utf-8") as f:
        env_spec = EnvironmentSpec.model_validate_json(f.read())
        
    llm_client = LLMClient(config)
    processor = DataProcessorAgent(llm_client)
    
    script = processor.generate_preprocessing_script(pka, manifest)
    
    process_dir = run_dir / "processing"
    process_dir.mkdir(parents=True, exist_ok=True)
    
    script_path = process_dir / "preprocess.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script.python_code)
        
    env = os.environ.copy()
    
    # Run the script using the conda env if available
    python_exec = "python"
    if env_spec.provisioning_status == "provisioned" and env_spec.conda_env_name:
        conda_env_dir = run_dir / "conda_env"
        # On Windows it's conda_env/python.exe, on Linux conda_env/bin/python
        win_path = conda_env_dir / "python.exe"
        linux_path = conda_env_dir / "bin" / "python"
        if win_path.exists():
            python_exec = str(win_path.resolve())
        elif linux_path.exists():
            python_exec = str(linux_path.resolve())
            
    try:
        result = subprocess.run(
            [python_exec, str(script_path)],
            env=env,
            cwd=str(process_dir),
            capture_output=True,
            text=True,
            timeout=config.execution.subprocess_timeout_seconds
        )
        
        execution_status = "completed" if result.returncode == 0 else "failed"
        stdout = result.stdout
        stderr = result.stderr
        
        if result.returncode != 0:
            logger.error(f"Preprocessing failed: {stderr}")
            
    except Exception as e:
        execution_status = "failed"
        stdout = ""
        stderr = str(e)
        logger.error(f"Execution error: {e}")
        
    artifact = ProcessedDatasetArtifact(
        paper_artifact_path=pka_path,
        data_manifest_path=data_manifest_path,
        environment_spec_path=env_spec_path,
        processed_datasets=[],
        preprocessing_execution=[
            ProcessingStepRecord(
                step_id="full_pipeline",
                code_path=str(script_path.resolve()),
                executed=True,
                execution_log_path=""
            )
        ],
        pipeline_code_path=str(script_path.resolve()),
        replicability_assessment="fully_faithful" if execution_status == "completed" else "partially_faithful",
        replicability_notes=""
    )
    
    output_path = run_dir / "processed_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(artifact.model_dump_json(indent=2))
        
    return PhaseResult(
        status="complete" if execution_status == "completed" else "blocked",
        artifact_path=str(output_path.resolve()),
        flags_raised=[stderr] if execution_status == "failed" else []
    )
