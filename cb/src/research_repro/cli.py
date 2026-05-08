import typer
import json
from pathlib import Path
from datetime import datetime
import re
from typing import Optional
import uuid

from research_repro.config import AppConfig
from research_repro.schemas.pipeline_state import PipelineState
from research_repro.orchestrator import build_orchestrator
from research_repro.logging_setup import setup_global_logger

app = typer.Typer()

@app.command()
def run(
    paper_input: str, 
    mode: str = typer.Option("auto", help="auto or interactive"),
    provider: str = typer.Option("ollama", help="Provider to use: 'ollama' or 'api'"),
    api_model: str = typer.Option("gemini-3.1-pro-preview", help="Model to use if provider is 'api'"),
    ollama_model: str = typer.Option("qwen3.5:4b", help="Model to use if provider is 'ollama'"),
    config_path: Optional[Path] = typer.Option(None, help="Path to config.json")
):
    # Setup run directory
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', paper_input.split('/')[-1])[:20]
    if not slug:
        slug = "paper"
    run_dir = Path("runs") / f"run_{ts}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Load config
    config = AppConfig()
    if config_path and config_path.exists():
        with open(config_path, "r") as f:
            cfg_dict = json.load(f)
            config = AppConfig(**cfg_dict)
            
    config.paper_input = paper_input
    config.run_directory = str(run_dir.resolve())
    config.mode = mode
    
    if provider == "ollama":
        config.llm_endpoint = "http://localhost:11434/v1"
        config.llm_model = ollama_model
        config.llm_api_key = "none"
    elif provider == "api":
        config.llm_model = api_model
        if config.llm_endpoint == "http://localhost:11434/v1":
            typer.echo("Warning: Provider set to 'api' but LLM_ENDPOINT in .env is still localhost. Make sure to set LLM_ENDPOINT and LLM_API_KEY in your .env file.", err=True)
    
    with open(run_dir / "config.json", "w") as f:
        f.write(config.model_dump_json(indent=2))
        
    setup_global_logger(str(run_dir.resolve()))
    
    # Initialize PipelineState
    state = PipelineState(
        run_id=str(uuid.uuid4()),
        run_directory=str(run_dir.resolve()),
        paper_input=paper_input,
        config_path=str((run_dir / "config.json").resolve()),
        mode=mode,
        phase_statuses=[],
        overall_status="initialized",
        last_updated=datetime.utcnow()
    )
    
    orchestrator = build_orchestrator()
    config_dict = {"configurable": {"thread_id": state.run_id}}
    
    typer.echo(f"Starting pipeline for {paper_input} in {run_dir}")
    
    # LangGraph streaming
    for event in orchestrator.stream({"state": state, "config": config}, config=config_dict):
        typer.echo(f"Transition: {list(event.keys())}")
        
    typer.echo("Pipeline run complete.")

@app.command()
def resume(run_dir: str):
    typer.echo(f"Resuming run from {run_dir}")
    # Not fully implemented for M2 yet, but stubbed as per spec

@app.command()
def inspect(run_dir: str):
    typer.echo(f"Inspecting run {run_dir}")
    # pretty-print phase outputs

if __name__ == "__main__":
    app()
