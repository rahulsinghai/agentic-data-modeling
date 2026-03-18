"""Profile command; run the profiler agent on source data."""

from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.rule import Rule

console = Console()


def profile_cmd(
    source_dir: Path = typer.Argument(..., help="Directory containing source data files"),
    output_dir: Path = typer.Option("output", help="Output directory for artifacts"),
) -> None:
    """Profile source data files and detect schemas, keys, and grain."""
    from langchain_core.messages import HumanMessage

    from agentic_data_modeling.agents.profiler import create_profiler_agent
    from agentic_data_modeling.cli.callbacks import PipelineCallbackHandler
    from agentic_data_modeling.tools.duckdb_tools import reset_connection

    reset_connection()

    handler = PipelineCallbackHandler(console)
    console.print(Rule("[bold]Profiling source data[/bold]", style="dim"))

    start = time.monotonic()
    agent = create_profiler_agent()
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=f"Profile all data files in: {source_dir.resolve()}"
                )
            ]
        },
        config={"callbacks": [handler]},
    )

    elapsed = time.monotonic() - start
    console.print(f"\n  [green]✓[/green] Profiling complete [dim]({elapsed:.1f}s)[/dim]")

    profiles = result["messages"][-1].content
    if profiles:
        out_path = output_dir / "profiles.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(profiles)
        console.print(f"Profiles → {out_path}")
