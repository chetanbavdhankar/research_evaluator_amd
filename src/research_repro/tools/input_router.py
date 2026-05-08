import httpx
import tempfile
from pathlib import Path
from research_repro.tools.document_types import ParsedPaper
from research_repro.tools.arxiv_fetcher import get_arxiv_id, fetch_arxiv_metadata, download_arxiv_pdf
from research_repro.tools.pdf_parser import parse_pdf
from research_repro.tools.html_parser import parse_html_url

def ingest_paper(input_str: str) -> ParsedPaper:
    arxiv_id = get_arxiv_id(input_str)
    
    if arxiv_id and arxiv_id != input_str:
        metadata = fetch_arxiv_metadata(arxiv_id)
        metadata["input_source"] = input_str
        
        html_url = f"https://arxiv.org/html/{arxiv_id}v1"
        try:
            response = httpx.head(html_url, follow_redirects=True)
            if response.status_code == 200:
                return parse_html_url(html_url, metadata)
        except Exception:
            pass
            
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = download_arxiv_pdf(arxiv_id, Path(tmpdir))
            return parse_pdf(str(pdf_path), metadata)
            
    elif input_str.startswith("http"):
        response = httpx.head(input_str, follow_redirects=True)
        content_type = response.headers.get("Content-Type", "")
        
        if "application/pdf" in content_type:
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = Path(tmpdir) / "downloaded.pdf"
                with open(pdf_path, 'wb') as f:
                    with httpx.stream("GET", input_str, follow_redirects=True) as stream_resp:
                        for chunk in stream_resp.iter_bytes():
                            f.write(chunk)
                return parse_pdf(str(pdf_path), {"input_source": input_str, "title": "Downloaded PDF", "authors": []})
        else:
            return parse_html_url(input_str, {"input_source": input_str, "title": "Web Page", "authors": []})
            
    else:
        path = Path(input_str)
        metadata = {"input_source": input_str, "title": path.stem, "authors": []}
        if path.suffix.lower() == ".pdf":
            return parse_pdf(str(path), metadata)
        elif path.suffix.lower() in [".html", ".htm"]:
            with open(path, "r", encoding="utf-8") as f:
                from research_repro.tools.html_parser import parse_html_content
                return parse_html_content(f.read(), metadata)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
