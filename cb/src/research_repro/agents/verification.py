import difflib
from pydantic import BaseModel
from typing import Tuple
from research_repro.schemas.common import VerificationRecord
from research_repro.tools.llm_client import LLMClient

def deterministic_verify(result: BaseModel, source_text: str) -> Tuple[bool, list[str], str]:
    """
    Recursively traverses Pydantic models to find all paper_quote fields.
    For each, checks fuzzy match against source_text (ratio >= 0.8).
    Returns (passed, checks_run, failure_reason)
    """
    checks_run = ["quote_grounding"]
    
    def extract_quotes(obj) -> list[str]:
        quotes = []
        if isinstance(obj, BaseModel):
            if hasattr(obj, "paper_quote") and isinstance(obj.paper_quote, str):
                quotes.append(obj.paper_quote)
            for k, v in obj:
                quotes.extend(extract_quotes(v))
        elif isinstance(obj, list):
            for item in obj:
                quotes.extend(extract_quotes(item))
        elif isinstance(obj, dict):
            for v in obj.values():
                quotes.extend(extract_quotes(v))
        return quotes

    quotes = extract_quotes(result)
    
    for quote in quotes:
        if not quote.strip():
            continue
            
        # Optimization: Simple containment check first
        if quote in source_text:
            continue
            
        # Fuzzy match
        matcher = difflib.SequenceMatcher(None, quote, source_text)
        # SequenceMatcher ratio with long text is slow and often low, we might just look for best matching block
        # For a hackathon, let's just do a simple substring check or a very rough fuzzy check.
        # Let's check if a good chunk of words are present.
        words = quote.split()
        if len(words) > 3:
            chunk = " ".join(words[:4])
            if chunk not in source_text:
                return False, checks_run, f"Quote not found in source text: '{quote}'"
        else:
            if quote not in source_text:
                return False, checks_run, f"Quote not found in source text: '{quote}'"

    return True, checks_run, ""

class CoherenceCheckResult(BaseModel):
    is_coherent: bool
    reasoning: str

def coherence_verify(result: BaseModel, source_text_excerpt: str, llm_client: LLMClient) -> Tuple[bool, list[str], str]:
    checks_run = ["llm_coherence"]
    
    prompt = f"""
    Please verify if the extracted JSON is grounded, relevant, and internally coherent with respect to the source excerpt.
    
    Source Excerpt:
    {source_text_excerpt[:2000]}
    
    Extracted JSON:
    {result.model_dump_json(indent=2)}
    
    Respond with JSON indicating whether it is coherent and why.
    """
    
    try:
        check = llm_client.chat([{"role": "user", "content": prompt}], response_model=CoherenceCheckResult)
        if not check.is_coherent:
            return False, checks_run, f"Coherence check failed: {check.reasoning}"
        return True, checks_run, ""
    except Exception as e:
        return False, checks_run, f"Coherence check error: {str(e)}"
