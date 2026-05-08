import os
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel
from research_repro.config import AppConfig
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.processed_dataset import ProcessedDatasetArtifact
from research_repro.schemas.environment_spec import EnvironmentSpec
from research_repro.schemas.analysis_results import AnalysisResultsPackage, MethodExecutionRecord
from research_repro.schemas.common import ExecutionFailure
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.analyzer import AnalyzerAgent
from research_repro.logging_setup import get_phase_logger
from research_repro.phases.phase1_paper_comprehension.executor import PhaseResult

def run(pka_path: str, processed_path: str, env_spec_path: str, run_dir: Path, config: AppConfig) -> PhaseResult:
    logger = get_phase_logger(str(run_dir), 5, "executor")
    logger.info(f"Starting Phase 5 for {pka_path}")
    
    with open(pka_path, "r", encoding="utf-8") as f:
        pka = PaperKnowledgeArtifact.model_validate_json(f.read())
        
    with open(processed_path, "r", encoding="utf-8") as f:
        processed = ProcessedDatasetArtifact.model_validate_json(f.read())
        
    with open(env_spec_path, "r", encoding="utf-8") as f:
        env_spec = EnvironmentSpec.model_validate_json(f.read())
        
    llm_client = LLMClient(config)
    analyzer = AnalyzerAgent(llm_client)
    
    script = analyzer.generate_analysis_script(pka, env_spec, processed)
    
    analysis_dir = run_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    script_path = analysis_dir / "analyze.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script.python_code)
        
    env = os.environ.copy()
    
    python_exec = "python"
    if env_spec.provisioning_status == "provisioned" and env_spec.conda_env_name:
        conda_env_dir = run_dir / "conda_env"
        win_path = conda_env_dir / "python.exe"
        linux_path = conda_env_dir / "bin" / "python"
        if win_path.exists():
            python_exec = str(win_path.resolve())
        elif linux_path.exists():
            python_exec = str(linux_path.resolve())
            
    num_runs = config.flags.max_seed_runs_when_unseeded if not env_spec.random_seeds else 1
    
    overall_status = "completed"
    method_results = []
    execution_logs = []
    failure_records = []
    
    for i in range(num_runs):
        seed_env = env.copy()
        if not env_spec.random_seeds:
            seed_env["RANDOM_SEED"] = str(42 + i)
            
        try:
            result = subprocess.run(
                [python_exec, str(script_path)],
                env=seed_env,
                cwd=str(analysis_dir),
                capture_output=True,
                text=True,
                timeout=config.execution.subprocess_timeout_seconds
            )
            
            if result.returncode != 0:
                logger.error(f"Analysis failed on run {i}: {result.stderr}")
                failure_records.append(ExecutionFailure(
                    failure_type="implementation_failure",
                    description=result.stderr,
                    resolution_status="unresolved",
                    resolution_attempted=False
                ))
                overall_status = "failed"
            else:
                results_json_path = analysis_dir / "results.json"
                if results_json_path.exists():
                    with open(results_json_path, "r", encoding="utf-8") as f:
                        res_data = json.load(f)
                        metrics = []
                        for k, v in res_data.items():
                            metrics.append({"name": k, "value": float(v), "split": "test"})
                            
                        method_results.append(MethodExecutionRecord(
                            method_id="Primary Method",
                            code_path=str(script_path.resolve()),
                            executed=True,
                            execution_log_path="",
                            runtime_seconds=0.0,
                            primary_outputs={"metrics": metrics}
                        ))
                
        except Exception as e:
            overall_status = "failed"
            logger.error(f"Execution error on run {i}: {e}")
            failure_records.append(ExecutionFailure(
                failure_type="implementation_failure",
                description=str(e),
                resolution_status="unresolved",
                resolution_attempted=False
            ))
            
    artifact = AnalysisResultsPackage(
        paper_artifact_path=pka_path,
        processed_dataset_path=processed_path,
        environment_spec_path=env_spec_path,
        method_executions=method_results,
        overall_status="complete" if overall_status == "completed" else "blocked"
    )
    
    output_path = run_dir / "analysis_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(artifact.model_dump_json(indent=2))
        
    return PhaseResult(
        status="complete" if overall_status == "completed" else "blocked",
        artifact_path=str(output_path.resolve()),
        flags_raised=[f.description for f in failure_records]
    )
