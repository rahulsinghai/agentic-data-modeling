"""Generate command; produce dbt, ERD, DDL, quality rules, docs."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

console = Console()

generate_app = typer.Typer(help="Generate artifacts from a dimensional model")


@generate_app.command("all")
def generate_all(
    model_path: Path = typer.Argument(..., help="Path to dimensional_model.json"),
    output_dir: Path = typer.Option("output", help="Output directory"),
) -> None:
    """Generate all artifacts: dbt models, ERD, DDL, quality rules, docs."""
    from agentic_data_modeling.agents.graph import compile_graph

    model_json = model_path.read_text()
    console.print("[bold]Generating all artifacts...[/bold]")

    graph = compile_graph()
    graph.invoke(
        {
            "messages": [],
            "source_dir": "",
            "output_dir": str(output_dir.resolve()),
            "requirements": "",
            "next_agent": "",
            "profiles_json": "",
            "model_json": model_json,
            "dbt_project_json": "",
            "quality_config_json": "",
            "artifacts": {},
            "completed_agents": ["profiler", "modeler"],
        },
        config={"recursion_limit": 50},
    )

    console.print("[green]All artifacts generated.[/green]")


@generate_app.command("dbt")
def generate_dbt(
    model_path: Path = typer.Argument(..., help="Path to dimensional_model.json"),
    output_dir: Path = typer.Option("output", help="Output directory"),
) -> None:
    """Generate dbt models only."""
    from agentic_data_modeling.agents.dbt_generator import dbt_generator_node

    model_json = model_path.read_text()
    console.print("[bold]Generating dbt models...[/bold]")

    dbt_generator_node(
        {
            "messages": [],
            "model_json": model_json,
            "output_dir": str(output_dir.resolve()),
            "source_dir": "",
            "requirements": "",
            "next_agent": "",
            "profiles_json": "",
            "dbt_project_json": "",
            "quality_config_json": "",
            "artifacts": {},
            "completed_agents": [],
        }
    )
    console.print("[green]dbt models generated.[/green]")


@generate_app.command("erd")
def generate_erd(
    model_path: Path = typer.Argument(..., help="Path to dimensional_model.json"),
    output_dir: Path = typer.Option("output", help="Output directory"),
) -> None:
    """Generate ERD diagram only."""
    from agentic_data_modeling.tools.codegen_tools import render_mermaid_erd

    model_json = model_path.read_text()
    console.print("[bold]Generating ERD...[/bold]")

    erd = render_mermaid_erd.invoke({"model_json": model_json})
    out_path = Path(output_dir) / "erd.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(f"```mermaid\n{erd}\n```\n")
    console.print(f"[green]ERD saved to: {out_path}[/green]")


@generate_app.command("ddl")
def generate_ddl(
    model_path: Path = typer.Argument(..., help="Path to dimensional_model.json"),
    output_dir: Path = typer.Option("output", help="Output directory"),
) -> None:
    """Generate DDL statements only."""
    from agentic_data_modeling.tools.codegen_tools import render_ddl

    model_json = model_path.read_text()
    console.print("[bold]Generating DDL...[/bold]")

    ddl = render_ddl.invoke({"model_json": model_json})
    out_path = Path(output_dir) / "ddl.sql"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ddl)
    console.print(f"[green]DDL saved to: {out_path}[/green]")
