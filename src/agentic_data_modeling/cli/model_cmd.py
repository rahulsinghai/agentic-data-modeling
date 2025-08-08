"""Model command — design dimensional model from requirements."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def model_cmd(
    requirements: str = typer.Argument(..., help="Business requirements or path to .md file"),
    source_dir: Path = typer.Option(None, help="Source data directory (for profiling first)"),
    output_dir: Path = typer.Option("output", help="Output directory"),
) -> None:
    """Design a dimensional model from business requirements."""
    from agentic_data_modeling.agents.graph import compile_graph

    # If requirements is a file path, read it
    req_path = Path(requirements)
    if req_path.exists() and req_path.is_file():
        requirements = req_path.read_text()

    console.print("[bold]Designing dimensional model...[/bold]")

    # If source_dir provided, start from profiling; otherwise skip to modeler
    completed = [] if source_dir else ["profiler"]

    graph = compile_graph()
    result = graph.invoke(
        {
            "messages": [],
            "source_dir": str(source_dir.resolve()) if source_dir else "",
            "output_dir": str(output_dir.resolve()),
            "requirements": requirements,
            "next_agent": "",
            "profiles_json": "",
            "model_json": "",
            "dbt_project_json": "",
            "quality_config_json": "",
            "artifacts": {},
            "completed_agents": completed,
        },
        config={"recursion_limit": 50},
    )

    console.print("[green]Modeling complete.[/green]")
    model_json = result.get("model_json", "")
    if model_json:
        out_path = output_dir / "dimensional_model.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(model_json)
        console.print(f"Model saved to: {out_path}")
