import pytest
import json
from pathlib import Path
from research_repro.config import AppConfig
from research_repro.phases.phase1_paper_comprehension.executor import run as phase1_run
from research_repro.schemas.paper_knowledge import PaperKnowledgeArtifact

def test_phase1_integration(fake_pdf_path, httpx_mock, tmp_path):
    # We must mock LLM responses for all the extraction steps
    
    config = AppConfig(llm_endpoint="http://dummy", llm_model="dummy", llm_api_key="none")
    
    def add_mock(payload):
        httpx_mock.add_response(
            json={
                "choices": [{"message": {"content": json.dumps(payload)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
        )

    # 1. extract_metadata
    add_mock({
        "title": "Fake Paper Title",
        "authors": ["Alice and Bob"],
        "input_source": ""
    })
    
    # 2. extract_summary
    add_mock({
        "abstract": "We investigate fake stuff.",
        "research_question": "Does fake work?",
        "domain": "fakeology",
        "claimed_contributions": ["did stuff"]
    })
    
    # 3. extract_datasets
    add_mock({"items": []})
    
    # 4. extract_preprocessing_pipeline
    add_mock({"items": []})
    
    # 5. extract_methodology
    add_mock({"items": []})
    
    # 6. extract_results
    add_mock({"items": []})
    
    # 7. extract_conclusions
    add_mock({"items": []})
    
    # 8. citation dependencies
    add_mock({"items": []})
    
    # 9. ambiguities
    add_mock({"items": []})
    
    # 10. risk assessment
    add_mock({"assessment": "Low risk"})

    run_dir = tmp_path / "run_dir"
    run_dir.mkdir()
    result = phase1_run(fake_pdf_path, run_dir, config)
    
    assert result.status == "complete"
    assert result.artifact_path.endswith("phase1_output.json")
    
    # Verify it can be loaded as PKA
    with open(result.artifact_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        pka = PaperKnowledgeArtifact.model_validate(data)
        assert pka.metadata.title == "Fake Paper Title"
        assert pka.summary.domain == "fakeology"
