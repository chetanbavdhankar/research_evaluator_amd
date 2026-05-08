import pytest
import json
from pathlib import Path
from unittest.mock import patch
from research_repro.config import AppConfig
from research_repro.phases.phase5_analysis_execution.executor import run as phase5_run
from research_repro.schemas.analysis_results import AnalysisResultsPackage

def test_phase5_integration(tmp_path, httpx_mock):
    config = AppConfig(llm_endpoint="http://dummy", llm_model="dummy", llm_api_key="none")
    run_dir = tmp_path / "run_dir"
    run_dir.mkdir()
    
    # Create dummy PKA
    pka_path = run_dir / "phase1_output.json"
    with open(pka_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "metadata": {"title": "Test", "authors": [], "input_source": ""},
            "summary": {"abstract": "", "research_question": "", "domain": "", "claimed_contributions": []},
            "datasets": [],
            "preprocessing_pipeline": [],
            "methodology": [],
            "results": [],
            "conclusions": [],
            "reproducibility_risk_assessment": ""
        }))
        
    processed_path = run_dir / "processed_dataset.json"
    with open(processed_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "paper_artifact_path": str(pka_path),
            "data_manifest_path": "",
            "environment_spec_path": "",
            "processed_datasets": [],
            "preprocessing_execution": [],
            "pipeline_code_path": "",
            "replicability_assessment": "fully_faithful",
            "replicability_notes": "",
            "intervention_flags": []
        }))
        
    env_spec_path = run_dir / "environment_spec.json"
    with open(env_spec_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "language": "Python",
            "language_version": "3.9",
            "dependencies": [],
            "dependency_conflicts": [],
            "hardware_gaps": [],
            "environment_assumptions": [],
            "environment_yml_path": "",
            "requirements_txt_path": None,
            "conda_env_name": "",
            "provisioning_status": "provisioned",
            "provisioning_errors": [],
            "reproducibility_target": {"target_type": "numerical", "justification": "", "numerical_tolerance": 0.01},
            "random_seeds": {}
        }))
        
    def add_mock(payload):
        httpx_mock.add_response(
            json={
                "choices": [{"message": {"content": json.dumps(payload)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
        )
        
    # generate_analysis_script
    add_mock({
        "python_code": 'import json\nwith open("results.json", "w") as f: json.dump({"accuracy": 0.95}, f)\n',
        "hyperparameter_defaults_assumed": {},
        "metric_ambiguities_resolved": []
    })
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        # Write dummy results.json because subprocess.run is mocked and won't actually write it
        analysis_dir = run_dir / "analysis"
        analysis_dir.mkdir(parents=True)
        with open(analysis_dir / "results.json", "w") as f:
            json.dump({"accuracy": 0.95}, f)
            
        result = phase5_run(str(pka_path), str(processed_path), str(env_spec_path), run_dir, config)
        
        assert result.status == "complete"
        
        with open(result.artifact_path, "r", encoding="utf-8") as f:
            artifact = AnalysisResultsPackage.model_validate_json(f.read())
            assert len(artifact.method_executions) > 0
