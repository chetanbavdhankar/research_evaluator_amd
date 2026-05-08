import os
import shutil
from pathlib import Path
import httpx
import arxiv
import urllib.parse
from rich.console import Console

console = Console()

def get_paper_dir(identifier: str) -> Path:
    d = Path("paper_audits") / identifier
    d.mkdir(parents=True, exist_ok=True)
    return d

def is_arxiv_id(paper: str) -> bool:
    return "." in paper and paper.replace(".", "").isdigit()

def is_url(paper: str) -> bool:
    return paper.startswith("http://") or paper.startswith("https://")

def download_arxiv(arxiv_id: str, dest_dir: Path) -> Path:
    filename = f"{arxiv_id}.pdf"
    pdf_path = dest_dir / filename
    
    try:
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(client.results(search))
        console.print(f"[blue]Found arXiv paper:[/blue] {paper.title}")
        paper.download_pdf(dirpath=str(dest_dir), filename=filename)
        return pdf_path
    except Exception as e:
        console.print(f"[yellow]arXiv API failed ({e}). Falling back to direct PDF download...[/yellow]")
        direct_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        with httpx.stream("GET", direct_url, follow_redirects=True) as response:
            response.raise_for_status()
            with open(pdf_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
        console.print(f"[blue]Directly downloaded arXiv PDF:[/blue] {direct_url}")
        return pdf_path

def download_pdf_url(url: str, dest_dir: Path) -> Path:
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename.endswith(".pdf"):
        filename = "downloaded_paper.pdf"
    
    pdf_path = dest_dir / filename
    console.print(f"[blue]Downloading PDF from URL:[/blue] {url}")
    
    with httpx.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        with open(pdf_path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    return pdf_path

def ingest_paper(paper_input: str) -> Path:
    """Ingest a paper from a local path, arXiv ID, or URL and return the local PDF path."""
    
    if os.path.exists(paper_input):
        paper_name = Path(paper_input).stem
        target_dir = get_paper_dir(paper_name) / "00_ingest"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_pdf = target_dir / f"{paper_name}.pdf"
        shutil.copy(paper_input, target_pdf)
        console.print(f"[green]Using local PDF file:[/green] {paper_input}")
        return target_pdf
    
    arxiv_id = None
    if is_arxiv_id(paper_input):
        arxiv_id = paper_input
    elif "arxiv.org/abs/" in paper_input:
        arxiv_id = paper_input.split("arxiv.org/abs/")[-1].split("v")[0]
    elif "arxiv.org/pdf/" in paper_input:
        arxiv_id = paper_input.split("arxiv.org/pdf/")[-1].replace(".pdf", "")
        
    if arxiv_id:
        target_dir = get_paper_dir(arxiv_id) / "00_ingest"
        target_dir.mkdir(parents=True, exist_ok=True)
        return download_arxiv(arxiv_id, target_dir)
        
    if is_url(paper_input):
        # Fallback for generic URLs
        paper_name = "url_paper"
        target_dir = get_paper_dir(paper_name) / "00_ingest"
        target_dir.mkdir(parents=True, exist_ok=True)
        return download_pdf_url(paper_input, target_dir)
        
    raise ValueError(f"Unrecognized paper input format or local file not found: {paper_input}")

def parse_pdf(pdf_path: Path):
    """Parse PDF and extract text."""
    import pymupdf
    console.print(f"[blue]Parsing PDF:[/blue] {pdf_path}")
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    console.print(f"Document has {len(doc)} pages. Extracted {len(text)} characters.")
    return {"pdf_path": str(pdf_path), "pages": len(doc), "text": text}
