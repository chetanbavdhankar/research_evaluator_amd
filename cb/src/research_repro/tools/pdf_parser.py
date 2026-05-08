import pymupdf
import re
from pathlib import Path
from research_repro.tools.document_types import ParsedPaper, FigureRef, TableRef

def parse_pdf(pdf_path: str, metadata: dict = None) -> ParsedPaper:
    if metadata is None:
        metadata = {}
        
    doc = pymupdf.open(pdf_path)
    
    pages = []
    figures = []
    tables = []
    
    # Basic extraction
    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        pages.append(text)
        
        # Simple heuristic to find figure/table captions in text
        # In a real implementation this would use layout info
        for line in text.split('\n'):
            line = line.strip()
            fig_match = re.match(r'^(?:Figure|Fig\.)\s*(\d+[a-zA-Z]?)\s*[:\.](.*)', line, re.IGNORECASE)
            if fig_match:
                figures.append(FigureRef(
                    id=fig_match.group(1),
                    caption=fig_match.group(2).strip(),
                    page_number=page_num + 1
                ))
            
            tab_match = re.match(r'^(?:Table)\s*(\d+[a-zA-Z]?)\s*[:\.](.*)', line, re.IGNORECASE)
            if tab_match:
                tables.append(TableRef(
                    id=tab_match.group(1),
                    caption=tab_match.group(2).strip(),
                    page_number=page_num + 1
                ))

    return ParsedPaper(
        pages=pages,
        figures=figures,
        tables=tables,
        metadata=metadata
    )
