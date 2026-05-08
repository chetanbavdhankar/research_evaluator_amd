import os
import json
from pathlib import Path
from rich.console import Console

console = Console()

def generate_scaffold(paper_dir: Path, audit_dict: dict, plan_markdown: str, exec_mode: bool):
    """Stage 5: Deterministic scaffold codegen."""
    console.print("\n[bold]Starting Stage 5: Scaffold Codegen[/bold]")
    
    tier = audit_dict.get("tier", 3)
    
    scaffold_dir = paper_dir / "05_scaffold"
    scaffold_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Base Artifacts
    with open(scaffold_dir / "AUDIT.json", "w", encoding="utf-8") as f:
        json.dump(audit_dict, f, indent=2)
        
    with open(scaffold_dir / "REPLICATION_PLAN.md", "w", encoding="utf-8") as f:
        f.write(plan_markdown)
        
    # GAPS.md
    with open(scaffold_dir / "GAPS.md", "w", encoding="utf-8") as f:
        f.write("# Gap Inventory\n\nReview the missing parameters and missing data sources here.\n")
        
    # DECISIONS.md
    with open(scaffold_dir / "DECISIONS.md", "w", encoding="utf-8") as f:
        f.write("# Replication Decisions\n\nLog any decisions made to substitute data or guess parameters.\n")
        
    console.print(f"[green]Created base artifacts in {scaffold_dir}/[/green]")
        
    # 2. Executable scripts
    if exec_mode:
        if tier == 3:
            console.print("[yellow]Skipping executable scaffold generation because paper is Tier 3 (Blocked).[/yellow]")
        else:
            scripts_dir = scaffold_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            data_dir = scaffold_dir / "data"
            data_dir.mkdir(exist_ok=True)
            with open(data_dir / ".gitkeep", "w", encoding="utf-8") as f:
                f.write("")
                
            # Python env
            with open(scaffold_dir / ".python-version", "w", encoding="utf-8") as f:
                f.write("3.12\n")
                
            # pyproject.toml
            deps = ["httpx", "pandas"]
            for soft in audit_dict.get("software_inventory", []):
                name = soft.get("name", "").lower()
                if name in ["numpy", "scipy", "astropy", "astroquery"]:
                    deps.append(name)
            
            pyproject_content = f'[project]\nname = "replication-{paper_dir.name}"\nversion = "0.1.0"\ndependencies = {json.dumps(list(set(deps)))}\n'
            with open(scaffold_dir / "pyproject.toml", "w", encoding="utf-8") as f:
                f.write(pyproject_content)
                
            # README.md
            with open(scaffold_dir / "README.md", "w", encoding="utf-8") as f:
                f.write(f"# Replication Scaffold: {paper_dir.name}\n\n**Tier**: {tier}\n\nSee REPLICATION_PLAN.md for next steps.")
            
            # Fetch scripts
            data_inv = audit_dict.get("data_inventory", [])
            for asset in data_inv:
                recipe = asset.get("download_recipe")
                if recipe and recipe.get("body"):
                    script_name = f"00_fetch_{asset['id']}.py" if recipe.get("language") == "python" else f"00_fetch_{asset['id']}.sh"
                    with open(scripts_dir / script_name, "w", encoding="utf-8") as f:
                        f.write(recipe["body"])
                    console.print(f" - Generated [blue]{scripts_dir / script_name}[/blue]")
                    
            # 01-04 Skeletons
            skeletons = {
                "01_preprocess.py": "def main():\n    # TODO: Implement preprocessing steps\n    pass\n\nif __name__ == '__main__':\n    main()\n",
                "02_analyze.py": "def main():\n    # TODO: Implement core analysis\n    pass\n\nif __name__ == '__main__':\n    main()\n",
                "03_compute_results.py": "def main():\n    # TODO: Generate final metrics\n    pass\n\nif __name__ == '__main__':\n    main()\n",
                "04_validate.py": "def main():\n    # TODO: Compare results against paper baseline tables\n    pass\n\nif __name__ == '__main__':\n    main()\n"
            }
            
            for name, content in skeletons.items():
                with open(scripts_dir / name, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            console.print("[green]Execution scaffold generation complete.[/green]")
