import pytest
from pydantic import ValidationError
from datetime import datetime
from research_repro.schemas.paper_knowledge import PaperMetadata, PaperSummary, PaperKnowledgeArtifact

def test_paper_knowledge_artifact_valid():
    metadata = PaperMetadata(
        title="Sample Title",
        authors=["Alice", "Bob"],
        input_source="https://arxiv.org/abs/1234.56789"
    )
    summary = PaperSummary(
        abstract="Sample abstract",
        research_question="Sample RQ",
        domain="computer vision",
        claimed_contributions=["Contrib 1"]
    )
    
    pka = PaperKnowledgeArtifact(
        metadata=metadata,
        summary=summary,
        datasets=[],
        preprocessing_pipeline=[],
        methodology=[],
        results=[],
        conclusions=["Concl 1"],
        reproducibility_risk_assessment="Low risk"
    )
    
    assert pka.metadata.title == "Sample Title"
    assert pka.summary.domain == "computer vision"

def test_paper_knowledge_artifact_invalid():
    metadata = PaperMetadata(
        title="Sample Title",
        authors=["Alice", "Bob"],
        input_source="https://arxiv.org/abs/1234.56789"
    )
    summary = PaperSummary(
        abstract="Sample abstract",
        research_question="Sample RQ",
        domain="computer vision",
        claimed_contributions=["Contrib 1"]
    )
    
    with pytest.raises(ValidationError):
        # Missing required conclusions and reproducibility_risk_assessment
        PaperKnowledgeArtifact(
            metadata=metadata,
            summary=summary,
            datasets=[],
            preprocessing_pipeline=[],
            methodology=[],
            results=[]
        )

def test_strict_mode():
    with pytest.raises(ValidationError):
        PaperMetadata(
            title="Title",
            authors=["Alice"],
            input_source="url",
            unknown_field="should fail"
        )
