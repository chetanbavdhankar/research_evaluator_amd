from typing import List
from rich.console import Console
from .models import DataAsset
from .adapters.base import DomainAdapter
from .adapters.astro import AstroAdapter
from .adapters.generic import GenericAdapter

console = Console()

def run_resolution(paper_text: str, data_assets: List[DataAsset]) -> List[DataAsset]:
    """Stage 2: Deterministic Resolution."""
    console.print("\n[bold]Starting Stage 2: Resolution (Adapters)[/bold]")
    
    adapters: List[DomainAdapter] = [AstroAdapter(), GenericAdapter()]
    
    # Sort adapters by applicability (detect) and priority
    adapters.sort(key=lambda a: (a.detect(paper_text), a.priority), reverse=True)
    active_adapters = [a for a in adapters if a.detect(paper_text) > 0.3]
    
    console.print(f"[blue]Active Adapters:[/blue] {[a.name for a in active_adapters]}")
    
    resolved_assets = []
    
    for asset in data_assets:
        resolved = False
        for adapter in active_adapters:
            result = adapter.resolve_dataset(asset, paper_text)
            asset.resolution_log.extend(result.log)
            
            if result.status == "resolved" and result.fetch_script:
                asset.download_recipe = result.fetch_script
                console.print(f" - [green]Resolved {asset.name} via {adapter.name} adapter.[/green]")
                resolved = True
                break
                
        if not resolved:
            console.print(f" - [yellow]Unresolved {asset.name}[/yellow]")
            
        resolved_assets.append(asset)
        
    return resolved_assets
