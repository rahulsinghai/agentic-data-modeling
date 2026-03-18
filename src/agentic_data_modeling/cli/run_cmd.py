"""Run command; full pipeline execution."""

from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.rule import Rule

console = Console()

_AGENT_LABELS: dict[str, str] = {
    "profiler": "Profiling source data",
    "modeler": "Designing dimensional model",
    "dbt_generator": "Generating dbt models",
    "doc_generator": "Generating ERD, DDL & docs",
    "quality_agent": "Generating data quality rules",
}


def run_cmd(
    requirements: str = typer.Argument(..., help="Business requirements or path to .md file"),
    source_dir: Path = typer.Option(..., help="Directory containing source data files"),
    output_dir: Path = typer.Option("output", help="Output directory for all artifacts"),
) -> None:
    """Run the full agentic data modeling pipeline end-to-end."""
    from agentic_data_modeling.agents.graph import compile_graph
    from agentic_data_modeling.cli.callbacks import PipelineCallbackHandler

    req_path = Path(requirements)
    if req_path.exists() and req_path.is_file():
        requirements = req_path.read_text()

    console.print(Rule("[bold blue]Agentic Data Modeling Pipeline[/bold blue]"))
    console.print(f"  Source : {source_dir}")
    console.print(f"  Output : {output_dir}")
    console.print(f"  Prompt : {requirements[:100].strip()}...")
    console.print()

    from agentic_data_modeling.tools.duckdb_tools import reset_connection

    reset_connection()
    graph = compile_graph()
    handler = PipelineCallbackHandler(console)
    final_state: dict = {}
    agent_start: float = 0.0
    pipeline_start = time.monotonic()

    for event in graph.stream(
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
        config={"recursion_limit": 100, "callbacks": [handler]},
    ):
        node_name = next(iter(event))
        state_update = event[node_name]
        final_state.update(state_update)

        if node_name == "router":
            next_agent = state_update.get("next_agent", "")
            label = _AGENT_LABELS.get(next_agent)
            if label:
                console.print(Rule(f"[bold]{label}[/bold]", style="dim"))
                agent_start = time.monotonic()
        else:
            label = _AGENT_LABELS.get(node_name, node_name)
            elapsed = time.monotonic() - agent_start
            console.print(
                f"\n  [green]✓[/green] {label} complete "
                f"[dim]({elapsed:.1f}s)[/dim]"
            )

    total = time.monotonic() - pipeline_start
    console.print()
    console.print(Rule(
        f"[bold green]Pipeline complete[/bold green] [dim]({total:.1f}s total)[/dim]"
    ))

    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    for key in ["profiles_json", "model_json", "dbt_project_json", "quality_config_json"]:
        content = final_state.get(key, "")
        if content:
            fname = key.replace("_json", "") + ".json"
            (output_dir / fname).write_text(content)
            saved.append(fname)

    if saved:
        console.print(f"Artifacts → [bold]{output_dir}/[/bold]: {', '.join(saved)}")
