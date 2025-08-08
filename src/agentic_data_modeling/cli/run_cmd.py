"""Run command — full pipeline execution."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def run_cmd(
    requirements: str = typer.Argument(..., help="Business requirements or path to .md file"),
    source_dir: Path = typer.Option(..., help="Directory containing source data files"),
    output_dir: Path = typer.Option("output", help="Output directory for all artifacts"),
) -> None:
    """Run the full agentic data modeling pipeline end-to-end."""
    from agentic_data_modeling.agents.graph import compile_graph

    # If requirements is a file path, read it
    req_path = Path(requirements)
    if req_path.exists() and req_path.is_file():
        requirements = req_path.read_text()

    console.print("[bold blue]Agentic Data Modeling Pipeline[/bold blue]")
    console.print(f"  Source: {source_dir}")
    console.print(f"  Output: {output_dir}")
    console.print(f"  Requirements: {requirements[:100]}...")
    console.print()

    graph = compile_graph()
    result = graph.invoke(
        {
            "messages": [],
            "source_dir": str(source_dir.resolve()),
            "output_dir": str(output_dir.resolve()),
            "requirements": requirements,
            "next_agent": "",
            "profiles_json": "",
            "model_json": "",
            "dbt_project_json": "",
            "quality_config_json": "",
            "artifacts": {},
            "completed_agents": [],
        },
        config={"recursion_limit": 100},
    )

    console.print()
    console.print("[bold green]Pipeline complete![/bold green]")

    # Save key outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    for key in ["profiles_json", "model_json", "dbt_project_json", "quality_config_json"]:
        content = result.get(key, "")
        if content:
            fname = key.replace("_json", "") + ".json"
            (output_dir / fname).write_text(content)

    console.print(f"Artifacts written to: {output_dir}")
