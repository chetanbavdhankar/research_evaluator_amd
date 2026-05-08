import pytest
import json
from pathlib import Path
from unittest.mock import patch
from research_repro.config import AppConfig
from research_repro.phases.phase4_data_processing.executor import run as phase4_run
from research_repro.schemas.processed_dataset import ProcessedDatasetArtifact

def test_phase4_integration(tmp_path, httpx_mock):
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
        
    manifest_path = run_dir / "data_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "paper_artifact_path": str(pka_path),
            "acquisitions": [],
            "overall_status": "all_acquired",
            "intervention_flags": [],
            "readiness_summary": ""
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
            "reproducibility_target": {"target_type": "exact", "justification": "", "numerical_tolerance": None},
            "random_seeds": {}
        }))
        
    def add_mock(payload):
        httpx_mock.add_response(
            json={
                "choices": [{"message": {"content": json.dumps(payload)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
        )
        
    # generate_preprocessing_script
    add_mock({
        "python_code": 'print("preprocessing")\n',
        "assumptions_made": []
    })
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "preprocessing"
        mock_run.return_value.stderr = ""
        
        result = phase4_run(str(pka_path), str(manifest_path), str(env_spec_path), run_dir, config)
        
        assert result.status == "complete"
        
        with open(result.artifact_path, "r", encoding="utf-8") as f:
            artifact = ProcessedDatasetArtifact.model_validate_json(f.read())
            assert artifact.replicability_assessment == "fully_faithful"
