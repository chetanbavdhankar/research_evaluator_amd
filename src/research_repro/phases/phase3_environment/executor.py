import os
import subprocess
from pathlib import Path
from research_repro.config import AppConfig
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact
from research_repro.schemas.environment_spec import EnvironmentSpec
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.environment import EnvironmentAgent
from research_repro.logging_setup import get_phase_logger
from research_repro.phases.phase1_paper_comprehension.executor import PhaseResult

def run(pka_path: str, run_dir: Path, config: AppConfig) -> PhaseResult:
    logger = get_phase_logger(str(run_dir), 3, "executor")
    logger.info(f"Starting Phase 3 for {pka_path}")
    
    with open(pka_path, "r", encoding="utf-8") as f:
        pka = PaperKnowledgeArtifact.model_validate_json(f.read())
        
    llm_client = LLMClient(config)
    env_agent = EnvironmentAgent(llm_client)
    
    inferred = env_agent.infer_dependencies(pka)
    hardware_map = env_agent.map_hardware(pka, "AMD MI300X, 192GB RAM, 128 cores")
    target = env_agent.determine_reproducibility_target(pka)
    
    env_name = f"repro_{run_dir.name}"
    yaml_result = env_agent.generate_environment_yml(inferred.dependencies, env_name)
    
    env_yml_path = run_dir / "environment.yml"
    with open(env_yml_path, "w", encoding="utf-8") as f:
        f.write(yaml_result.yaml_content)
        
    conda_env_dir = run_dir / "conda_env"
    
    provisioning_status = "provisioned"
    provisioning_errors = []
    
    try:
        # Run conda env create
        result = subprocess.run(
            ["conda", "env", "create", "-f", str(env_yml_path), "-p", str(conda_env_dir)],
            capture_output=True,
            text=True,
            timeout=config.execution.subprocess_timeout_seconds
        )
        if result.returncode != 0:
            logger.error(f"Conda env creation failed: {result.stderr}")
            provisioning_status = "failed"
            provisioning_errors.append(result.stderr)
    except FileNotFoundError:
        logger.warning("conda command not found. Skipping actual provisioning for this run.")
        provisioning_status = "failed"
        provisioning_errors.append("conda command not found")
    except Exception as e:
        logger.error(f"Failed to run conda: {e}")
        provisioning_status = "failed"
        provisioning_errors.append(str(e))
        
    spec = EnvironmentSpec(
        language="Python",
        language_version=inferred.python_version,
        dependencies=inferred.dependencies,
        dependency_conflicts=[],
        hardware_gaps=hardware_map.hardware_gaps,
        environment_assumptions=inferred.environment_assumptions,
        environment_yml_path=str(env_yml_path.resolve()),
        requirements_txt_path=None,
        conda_env_name=env_name,
        provisioning_status=provisioning_status,
        provisioning_errors=provisioning_errors,
        reproducibility_target=target.target,
        random_seeds={}
    )
    
    output_path = run_dir / "environment_spec.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(spec.model_dump_json(indent=2))
        
    status = "complete" if provisioning_status == "provisioned" else "blocked"
    return PhaseResult(
        status=status,
        artifact_path=str(output_path.resolve()),
        flags_raised=provisioning_errors
    )
