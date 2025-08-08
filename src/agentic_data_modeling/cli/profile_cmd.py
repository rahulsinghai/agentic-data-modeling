"""Profile command — run the profiler agent on source data."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()


def profile_cmd(
    source_dir: Path = typer.Argument(..., help="Directory containing source data files"),
    output_dir: Path = typer.Option("output", help="Output directory for artifacts"),
) -> None:
    """Profile source data files and detect schemas, keys, and grain."""
    from agentic_data_modeling.agents.graph import compile_graph

    console.print(f"[bold]Profiling data in:[/bold] {source_dir}")

    graph = compile_graph()
    result = graph.invoke(
        {
            "messages": [],
            "source_dir": str(source_dir.resolve()),
            "output_dir": str(output_dir.resolve()),
            "requirements": "",
            "next_agent": "",
            "profiles_json": "",
            "model_json": "",
            "dbt_project_json": "",
            "quality_config_json": "",
            "artifacts": {},
            "completed_agents": [],
        },
        config={"recursion_limit": 50},
    )

    # Only run profiler — stop after it
    console.print("[green]Profiling complete.[/green]")
    profiles = result.get("profiles_json", "")
    if profiles:
        out_path = output_dir / "profiles.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(profiles)
        console.print(f"Profiles saved to: {out_path}")
