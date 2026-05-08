import pytest
import os
from pathlib import Path
from reportlab.pdfgen import canvas

@pytest.fixture(scope="session")
def fake_pdf_path():
    fixtures_dir = Path(__file__).parent / "fixtures" / "papers"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = fixtures_dir / "fake_paper.pdf"
    
    if not pdf_path.exists():
        c = canvas.Canvas(str(pdf_path))
        c.drawString(100, 800, "Fake Paper Title")
        c.drawString(100, 780, "Alice and Bob")
        c.drawString(100, 760, "Abstract: We investigate fake stuff.")
        c.showPage()
        c.drawString(100, 800, "Methodology: We did stuff using a dataset.")
        c.drawString(100, 780, "We used a neural network.")
        c.save()
        
    return str(pdf_path)

@pytest.fixture
def mock_llm_json(httpx_mock):
    def _mock_response(json_response):
        httpx_mock.add_response(
            json={
                "choices": [{"message": {"content": json_response}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
            }
        )
    return _mock_response

import logging

@pytest.fixture(autouse=True)
def cleanup_loggers():
    yield
    for logger_name in list(logging.root.manager.loggerDict.keys()):
        logger = logging.getLogger(logger_name)
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)
    for handler in list(logging.root.handlers):
        handler.close()
        logging.root.removeHandler(handler)

