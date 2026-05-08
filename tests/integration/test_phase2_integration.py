import pytest
import json
from pathlib import Path
from unittest.mock import patch
from research_repro.config import AppConfig
from research_repro.phases.phase2_data_sourcing.executor import run as phase2_run
from research_repro.schemas.data_manifest import DataManifest
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact, DatasetDescription

def test_phase2_integration(tmp_path, httpx_mock):
    config = AppConfig(llm_endpoint="http://dummy", llm_model="dummy", llm_api_key="none")
    run_dir = tmp_path / "run_dir"
    run_dir.mkdir()
    
    # Create dummy PKA
    pka_path = run_dir / "phase1_output.json"
    with open(pka_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "metadata": {"title": "Test", "authors": [], "input_source": ""},
            "summary": {"abstract": "", "research_question": "", "domain": "", "claimed_contributions": []},
            "datasets": [
                {"name": "Dataset A", "description": "Public dataset", "source_type": "public_specified"}
            ],
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
        
    # Mock classify_dataset
    add_mock({
        "category": "A_public_specified",
        "reasoning": "Clear description",
        "search_query_if_needed": ""
    })
    
    # Mock generate_download_script
    add_mock({
        "python_code": 'import os\nwith open("test.txt", "w") as f: f.write("data")\n',
        "required_packages": []
    })
    
    # We patch subprocess.run to avoid executing untrusted code or depending on local env too much
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        
        result = phase2_run(str(pka_path), run_dir, config)
        
        assert result.status == "complete"
        
        # Verify Manifest
        with open(result.artifact_path, "r", encoding="utf-8") as f:
            manifest = DataManifest.model_validate_json(f.read())
            assert manifest.overall_status == "all_acquired"
            assert len(manifest.acquisitions) == 1
            assert manifest.acquisitions[0].status == "acquired"
