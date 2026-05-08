import json
import httpx
from pathlib import Path
from rich.console import Console
from .models import DataAsset, MethodStep, Software, ComputeFootprint
from google import genai
from pydantic import TypeAdapter
from typing import List

console = Console()

def load_prompt(prompt_name: str, text: str) -> str:
    prompt_path = Path("prompts/extraction") / f"{prompt_name}.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{text}", text[:30000])

def call_gemini(api_key: str, model_name: str, prompt: str):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
    )
    return response.text

def call_ollama(model_name: str, prompt: str):
    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0,
                "num_ctx": 96000
            }
        },
        timeout=240.0
    )
    response.raise_for_status()
    text = response.json()["response"].strip()
    
    # Qwen sometimes wraps in markdown even with format=json
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    return text.strip()

def run_single_extraction(llm_settings: dict, prompt_name: str, text: str, schema_adapter):
    prompt = load_prompt(prompt_name, text)
    console.print(f"[blue]Running {prompt_name} extraction with {llm_settings['model']}...[/blue]")
    try:
        if llm_settings["type"] == "api":
            result_json = call_gemini(llm_settings["api_key"], llm_settings["model"], prompt)
        else:
            result_json = call_ollama(llm_settings["model"], prompt)
        return schema_adapter.validate_json(result_json)
    except Exception as e:
        console.print(f"[red]Failed extraction for {prompt_name}: {e}[/red]")
        return [] if "List" in str(schema_adapter) else None

def run_extraction(llm_settings: dict, paper_text: str) -> dict:
    """Run the extraction pipeline across all 4 domains."""
    return {
        "data_inventory": run_single_extraction(llm_settings, "extract_data", paper_text, TypeAdapter(List[DataAsset])),
        "method_pipeline": run_single_extraction(llm_settings, "extract_methods", paper_text, TypeAdapter(List[MethodStep])),
        "software_inventory": run_single_extraction(llm_settings, "extract_software", paper_text, TypeAdapter(List[Software])),
        "compute_estimate": run_single_extraction(llm_settings, "extract_compute", paper_text, TypeAdapter(ComputeFootprint))
    }
