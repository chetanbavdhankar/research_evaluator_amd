import typer
import json
from pathlib import Path
from rich.console import Console
from .llm_config import configure_llm
from .ingest import ingest_paper, parse_pdf
from .extraction import run_extraction
from .resolution import run_resolution
from .scoring import generate_scorecard, derive_tier
from .planning import synthesize_prose, generate_plan_markdown
from .scaffold import generate_scaffold

app = typer.Typer(help="Replicability Audit CLI for Research Papers")
console = Console()

def run_pipeline(paper: str, llm_settings: dict, run_plan: bool = False, exec_mode: bool = False):
    try:
        # STAGE 0: Ingest
        pdf_path = ingest_paper(paper)
        paper_name = Path(pdf_path).stem
        paper_dir = Path("paper_audits") / paper_name
        console.print(f"[bold green]Successfully retrieved PDF:[/bold green] {pdf_path}")
        
        parsed_data = parse_pdf(pdf_path)
        
        # STAGE 1: Extraction
        console.print("\n[bold]Starting Stage 1: LLM Extraction...[/bold]")
        audit_dict = run_extraction(llm_settings, parsed_data["text"])
        
        console.print("\n[bold green]Extraction Complete. Summary:[/bold green]")
        data_inv = audit_dict.get("data_inventory") or []
        console.print(f" - [bold]{len(data_inv)}[/bold] Data Assets")
        method_inv = audit_dict.get("method_pipeline") or []
        console.print(f" - [bold]{len(method_inv)}[/bold] Method Steps")
        soft_inv = audit_dict.get("software_inventory") or []
        console.print(f" - [bold]{len(soft_inv)}[/bold] Software/Code references")
        
        ex_dir = paper_dir / "01_extract"
        ex_dir.mkdir(exist_ok=True)
        with open(ex_dir / "extracted.json", "w") as f:
            # We don't have pydantic dumps yet, just raw dictionaries if we want, but wait, audit_dict has pydantic models.
            pass
        
        # STAGE 2: Resolution
        resolved_data_inv = run_resolution(parsed_data["text"], data_inv)
        
        serializable_audit = {
            "data_inventory": [a.model_dump(mode="json") for a in resolved_data_inv],
            "method_pipeline": [m.model_dump(mode="json") for m in method_inv],
            "software_inventory": [s.model_dump(mode="json") for s in soft_inv],
            "compute_estimate": audit_dict.get("compute_estimate").model_dump(mode="json") if audit_dict.get("compute_estimate") else None
        }
        
        res_dir = paper_dir / "02_resolve"
        res_dir.mkdir(exist_ok=True)
        with open(res_dir / "resolved.json", "w") as f:
            json.dump(serializable_audit, f, indent=2)
            
        # STAGE 3: Scoring
        console.print("\n[bold]Starting Stage 3: Scoring[/bold]")
        scorecard = generate_scorecard(serializable_audit)
        tier = derive_tier(scorecard)
        serializable_audit["scorecard"] = scorecard
        serializable_audit["tier"] = tier
        
        console.print(f"[bold blue]Replicability Tier:[/bold blue] {tier}")
        for axis, score in scorecard.items():
            console.print(f" - {axis}: {score}/3")
            
        score_dir = paper_dir / "03_score"
        score_dir.mkdir(exist_ok=True)
        with open(score_dir / "scored.json", "w") as f:
            json.dump(serializable_audit, f, indent=2)

        if not run_plan:
            return

        # STAGE 4: Planning
        prose = synthesize_prose(llm_settings, serializable_audit)
        plan_markdown = generate_plan_markdown(serializable_audit, prose)
        
        plan_dir = paper_dir / "04_plan"
        plan_dir.mkdir(exist_ok=True)
        with open(plan_dir / "REPLICATION_PLAN.md", "w", encoding="utf-8") as f:
            f.write(plan_markdown)
        
        # STAGE 5: Scaffold Codegen
        generate_scaffold(paper_dir, serializable_audit, plan_markdown, exec_mode)

    except Exception as e:
        console.print(f"[bold red]Error during pipeline execution:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def ingest(paper: str = typer.Argument(..., help="Path to local PDF, arXiv ID, or URL")):
    """Stage 0..3: Parse, extract, resolve, and score."""
    console.print("\n[bold]Configuring LLM Settings...[/bold]")
    llm_settings = configure_llm()
    console.print(f"\n[bold green]Starting pipeline with LLM:[/bold green] {llm_settings['type']} ({llm_settings['model']})")
    run_pipeline(paper, llm_settings, run_plan=False)

@app.command()
def plan(
    paper: str = typer.Argument(..., help="Path to local PDF, arXiv ID, or URL"),
    exec: bool = typer.Option(False, "--exec", help="Generate executable scaffold directory")
):
    """Stage 0..5: Audit + plan + scaffold."""
    console.print("\n[bold]Configuring LLM Settings...[/bold]")
    llm_settings = configure_llm()
    console.print(f"\n[bold green]Starting full plan pipeline with LLM:[/bold green] {llm_settings['type']} ({llm_settings['model']})")
    run_pipeline(paper, llm_settings, run_plan=True, exec_mode=exec)

if __name__ == "__main__":
    app()
