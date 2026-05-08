import arxiv
import os
import re
import urllib.request
from pathlib import Path
from typing import Tuple, Dict, Any

def get_arxiv_id(url_or_id: str) -> str:
    # Match arxiv.org URLs or plain IDs
    match = re.search(r'(?:arxiv\.org/(?:abs|pdf|html)/)?(\d{4}\.\d{4,5}(?:v\d+)?)', url_or_id)
    if match:
        return match.group(1)
    return url_or_id

def fetch_arxiv_metadata(arxiv_id: str) -> Dict[str, Any]:
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(client.results(search))
    if not results:
        return {}
    
    paper = results[0]
    return {
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "published": paper.published.isoformat() if paper.published else None,
        "summary": paper.summary,
        "pdf_url": paper.pdf_url,
        "arxiv_id": arxiv_id,
    }

def download_arxiv_pdf(arxiv_id: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = dest_dir / f"{arxiv_id}.pdf"
    
    # Check if we can use the library
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(client.results(search))
    
    if results:
        results[0].download_pdf(dirpath=str(dest_dir), filename=f"{arxiv_id}.pdf")
        return pdf_path
    
    # Fallback for very new papers that arxiv library might fail to fetch
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    urllib.request.urlretrieve(pdf_url, str(pdf_path))
    return pdf_path
