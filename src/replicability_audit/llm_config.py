import subprocess
import os
import typer
from rich.console import Console

console = Console()

def get_installed_ollama_models():
    """Retrieve a list of installed models from local ollama."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        models = []
        if len(lines) > 1:
            for line in lines[1:]: # Skip header
                parts = line.split()
                if parts:
                    models.append(parts[0])
        return models
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def configure_llm():
    """Interactive prompt to configure LLM settings."""
    use_api = typer.confirm("Do you want to use an external API (Google Gemini) instead of a local LLM?", default=False)
    
    if use_api:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_google_gemini_api_key_here":
            console.print("[bold red]Warning: GEMINI_API_KEY is not set or is using the default placeholder in the .env file.[/bold red]")
            console.print("Please update the .env file with your actual API key.")
            
        model = typer.prompt("Enter the API model to use", default="gemini-3.1-pro-preview")
        console.print(f"[bold green]Selected API model:[/bold green] {model}")
        return {"type": "api", "model": model, "api_key": api_key}
    else:
        installed_models = get_installed_ollama_models()
        default_local = "qwen3.5:4b"
        
        if installed_models:
            console.print("\n[bold]Installed Local Models (Ollama):[/bold]")
            for m in installed_models:
                console.print(f" - {m}")
        else:
            console.print("\n[yellow]No local Ollama models found or Ollama is not installed/running.[/yellow]")
            
        model = typer.prompt("Enter the local model to use", default=default_local)
        console.print(f"[bold green]Selected local model:[/bold green] {model}")
        return {"type": "local", "model": model}
