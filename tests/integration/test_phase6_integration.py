import pytest
import json
from pathlib import Path
from unittest.mock import patch
from research_repro.config import AppConfig
from research_repro.phases.phase6_results_validation.executor import run as phase6_run
from research_repro.schemas.reproducibility_report import ReproducibilityReport

def test_phase6_integration(tmp_path, httpx_mock):
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
            "results": [
                {
                    "result_id": "res_1",
                    "description": "Accuracy test",
                    "metric_name": "accuracy",
                    "reported_value": 0.95,
                    "method_id": "m1",
                    "dataset_split": "test",
                    "location_in_paper": "Section 4",
                    "figure_or_table": "Table 1"
                }
            ],
            "conclusions": [
                "Our method achieves 95% accuracy"
            ],
            "reproducibility_risk_assessment": ""
        }))
        
    analysis_path = run_dir / "analysis_results.json"
    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "paper_artifact_path": str(pka_path),
            "processed_dataset_path": "",
            "environment_spec_path": "",
            "method_executions": [
                {
                    "method_id": "Primary",
                    "code_path": "",
                    "executed": True,
                    "execution_log_path": "",
                    "runtime_seconds": 1.0,
                    "primary_outputs": {
                        "metrics": [
                            {"name": "accuracy", "value": 0.94, "split": "test"}
                        ]
                    }
                }
            ],
            "overall_status": "complete",
            "intervention_flags": []
        }))
        
    def add_mock(payload):
        httpx_mock.add_response(
            json={
                "choices": [{"message": {"content": json.dumps(payload)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
        )
        
    # evaluate_discrepancy
    add_mock({
        "candidate_causes": ["Missing random seed"],
        "most_likely_cause": "Missing random seed",
        "classification": "explained",
        "notes": ""
    })
    
    # assess_claim
    add_mock({
        "assessment": "partially_supported",
        "rationale": "94% is close to 95%"
    })
    
    # generate_narrative
    add_mock({
        "executive_summary": "Summary",
        "overall_score": "moderate",
        "overall_score_justification": "Almost exact match",
        "recommendations": []
    })
    
    result = phase6_run(str(pka_path), str(analysis_path), run_dir, config)
    
    assert result.status == "complete"
    
    with open(result.artifact_path, "r", encoding="utf-8") as f:
        report = ReproducibilityReport.model_validate_json(f.read())
        assert report.overall_score == "moderate"
        assert len(report.result_comparisons) == 1
        assert report.result_comparisons[0].classification == "moderate_discrepancy"
