import pytest
import json
from pathlib import Path
from unittest.mock import patch
from research_repro.config import AppConfig
from research_repro.phases.phase3_environment.executor import run as phase3_run
from research_repro.schemas.environment_spec import EnvironmentSpec

def test_phase3_integration(tmp_path, httpx_mock):
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
        
    def add_mock(payload):
        httpx_mock.add_response(
            json={
                "choices": [{"message": {"content": json.dumps(payload)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
        )
        
    # infer_dependencies
    add_mock({
        "dependencies": [{"name": "numpy", "version": "1.21", "confidence": "confirmed", "inference_reasoning": ""}],
        "environment_assumptions": [],
        "python_version": "3.9"
    })
    
    # map_hardware
    add_mock({
        "hardware_gaps": []
    })
    
    # determine_reproducibility_target
    add_mock({
        "target": {"target_type": "numerical", "justification": "", "numerical_tolerance": 0.01}
    })
    
    # generate_environment_yml
    add_mock({
        "yaml_content": "name: test\ndependencies:\n  - numpy=1.21"
    })
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        result = phase3_run(str(pka_path), run_dir, config)
        
        assert result.status == "complete"
        
        with open(result.artifact_path, "r", encoding="utf-8") as f:
            spec = EnvironmentSpec.model_validate_json(f.read())
            assert spec.language_version == "3.9"
            assert spec.provisioning_status == "provisioned"
            assert "test" in spec.environment_yml_path or "run_dir" in spec.environment_yml_path
