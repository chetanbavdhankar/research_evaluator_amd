import json
from pathlib import Path
from rich.console import Console
import jinja2
from .extraction import call_gemini, call_ollama

console = Console()

def synthesize_prose(llm_settings: dict, audit_dict: dict) -> dict:
    console.print("\n[bold]Starting Stage 4: Plan Synthesis...[/bold]")
    
    prompt_path = Path("prompts/plan/prose_synthesis.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
        
    prompt = prompt_template.replace("{audit_json}", json.dumps(audit_dict))
    
    try:
        if llm_settings["type"] == "api":
            result_json = call_gemini(llm_settings["api_key"], llm_settings["model"], prompt)
        else:
            result_json = call_ollama(llm_settings["model"], prompt)
            
        return json.loads(result_json)
    except Exception as e:
        console.print(f"[red]Failed plan prose synthesis: {e}[/red]")
        return {
            "executive_summary": "Failed to generate summary.",
            "gap_synthesis": "Failed to generate gap analysis.",
            "substitution_suggestions": "Failed to generate suggestions."
        }

def generate_plan_markdown(audit_dict: dict, prose: dict) -> str:
    tier = audit_dict.get("tier", 3)
    template_path = Path("templates/plan") / f"tier{tier}.md.j2"
    
    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()
        
    template = jinja2.Template(template_str)
    
    context = {
        "scorecard": audit_dict.get("scorecard", {}),
        **prose
    }
    return template.render(context)
