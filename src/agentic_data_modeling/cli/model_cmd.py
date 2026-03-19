"""Model command; design dimensional model from requirements."""

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
    "router": None,
    "profiler": "Profiling source data",
    "modeler": "Designing dimensional model",
}


def model_cmd(
    requirements: str = typer.Argument(..., help="Business requirements or path to .md file"),
    source_dir: Path = typer.Option(None, help="Source data directory (for profiling first)"),
    output_dir: Path = typer.Option("output", help="Output directory"),
) -> None:
    """Design a dimensional model from business requirements."""
    from agentic_data_modeling.agents.graph import compile_graph

    req_path = Path(requirements)
    if req_path.exists() and req_path.is_file():
        requirements = req_path.read_text()

    console.print("[bold]Designing dimensional model...[/bold]")

    completed = [] if source_dir else ["profiler"]
    graph = compile_graph()
    final_state: dict = {}
    start = time.monotonic()

    with Live(console=console, refresh_per_second=10) as live:
        for event in graph.stream(
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
        ):
            node_name = next(iter(event))
            state_update = event[node_name]
            final_state.update(state_update)

            label = _AGENT_LABELS.get(node_name)
            if label is None:
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
                elapsed = time.monotonic() - start
                live.update(Text(""))
                console.print(f"  [green]✓[/green] {label} [dim]({elapsed:.1f}s)[/dim]")

    model_json = final_state.get("model_json", "")
    if model_json:
        out_path = output_dir / "dimensional_model.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(model_json)
        console.print(f"Model saved to: {out_path}")
