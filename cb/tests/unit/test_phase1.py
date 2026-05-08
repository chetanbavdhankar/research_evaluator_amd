import pytest
import json
from research_repro.config import AppConfig
from research_repro.tools.llm_client import LLMClient
from research_repro.agents.reader import ReaderAgent
from research_repro.tools.document_types import ParsedPaper, FigureRef, TableRef

def test_reader_extract_metadata(mock_llm_json):
    config = AppConfig(llm_endpoint="http://dummy", llm_model="dummy", llm_api_key="none")
    client = LLMClient(config)
    reader = ReaderAgent(client)
    
    mock_llm_json(json.dumps({
        "title": "Fake Title",
        "authors": ["Alice"],
        "input_source": ""
    }))
    
    parsed = ParsedPaper(pages=["Fake Title\nAlice"], figures=[], tables=[], metadata={})
    
    meta = reader.extract_metadata(parsed)
    assert meta.title == "Fake Title"
