import urllib.request
import httpx
from bs4 import BeautifulSoup
from research_repro.tools.document_types import ParsedPaper, FigureRef, TableRef

def parse_html_url(url: str, metadata: dict = None) -> ParsedPaper:
    if metadata is None:
        metadata = {}
        
    # We use httpx to fetch the HTML
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.raise_for_status()
    
    return parse_html_content(response.text, metadata)

def parse_html_content(html_content: str, metadata: dict = None) -> ParsedPaper:
    if metadata is None:
        metadata = {}
        
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Try to extract sections as pages to keep chunking manageable
    pages = []
    
    # Naive extraction: just get text blocks. ArXiv HTML has specific structure we could target.
    # For now, let's extract sections if possible, else just chunk the body.
    sections = soup.find_all(['section', 'div'], class_=['ltx_section', 'ltx_chapter'])
    if sections:
        for sec in sections:
            pages.append(sec.get_text(separator='\n', strip=True))
    else:
        # Fallback to just the body text chunked
        body = soup.find('body')
        text = body.get_text(separator='\n', strip=True) if body else soup.get_text(separator='\n', strip=True)
        # Split into roughly 3000 character chunks
        chunk_size = 3000
        pages = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
    figures = []
    tables = []
    
    # Extract figures
    fig_elements = soup.find_all(['figure', 'div'], class_=['ltx_figure'])
    for idx, fig in enumerate(fig_elements):
        caption = fig.find('figcaption')
        caption_text = caption.get_text(strip=True) if caption else ""
        figures.append(FigureRef(
            id=str(idx+1),
            caption=caption_text,
            page_number=1
        ))
        
    # Extract tables
    tab_elements = soup.find_all(['table', 'div'], class_=['ltx_table'])
    for idx, tab in enumerate(tab_elements):
        caption = tab.find('caption')
        caption_text = caption.get_text(strip=True) if caption else ""
        tables.append(TableRef(
            id=str(idx+1),
            caption=caption_text,
            page_number=1,
            content=tab.get_text(separator='\n', strip=True)
        ))

    return ParsedPaper(
        pages=pages,
        figures=figures,
        tables=tables,
        metadata=metadata
    )
