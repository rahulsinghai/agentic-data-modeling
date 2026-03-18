"""Run command; full pipeline execution."""

from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text

console = Console()

_AGENT_LABELS = {
    "router": None,  # internal, don't surface
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

    req_path = Path(requirements)
    if req_path.exists() and req_path.is_file():
        requirements = req_path.read_text()

    console.print("[bold blue]Agentic Data Modeling Pipeline[/bold blue]")
    console.print(f"  Source : {source_dir}")
    console.print(f"  Output : {output_dir}")
    console.print(f"  Prompt : {requirements[:100].strip()}...")
    console.print()

    graph = compile_graph()
    final_state: dict = {}
    completed: list[str] = []
    start = time.monotonic()

    with Live(console=console, refresh_per_second=10) as live:
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
            config={"recursion_limit": 100},
        ):
            # Each event is {node_name: state_update}
            node_name = next(iter(event))
            state_update = event[node_name]
            final_state.update(state_update)

            label = _AGENT_LABELS.get(node_name)
            if label is None:
                # router fired; show spinner for next agent
                next_agent = state_update.get("next_agent", "")
                next_label = _AGENT_LABELS.get(next_agent, "")
                if next_label:
                    live.update(
                        Text.assemble(
                            Spinner("dots").render(time.monotonic()),
                            f"  {next_label}...",
                        )
                    )
            else:
                # agent completed; print a done line and clear spinner
                elapsed = time.monotonic() - start
                live.update(Text(""))
                console.print(
                    f"  [green]✓[/green] {label} "
                    f"[dim]({elapsed:.1f}s)[/dim]"
                )
                completed.append(node_name)

    total = time.monotonic() - start
    console.print()
    console.print(f"[bold green]Pipeline complete[/bold green] [dim]({total:.1f}s total)[/dim]")

    # Persist key outputs
    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    for key in ["profiles_json", "model_json", "dbt_project_json", "quality_config_json"]:
        content = final_state.get(key, "")
        if content:
            fname = key.replace("_json", "") + ".json"
            (output_dir / fname).write_text(content)
            saved.append(fname)

    if saved:
        console.print(f"Artifacts saved to [bold]{output_dir}/[/bold]: {', '.join(saved)}")
