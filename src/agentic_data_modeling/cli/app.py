"""Main CLI application."""

from __future__ import annotations

import typer

from agentic_data_modeling.cli.generate_cmd import generate_app
from agentic_data_modeling.cli.model_cmd import model_cmd
from agentic_data_modeling.cli.profile_cmd import profile_cmd
from agentic_data_modeling.cli.run_cmd import run_cmd

app = typer.Typer(
    name="adm",
    help="Agentic Data Modeling — AI-powered dimensional modeling pipeline",
    no_args_is_help=True,
)

app.command("profile")(profile_cmd)
app.command("model")(model_cmd)
app.add_typer(generate_app, name="generate")
app.command("run")(run_cmd)


if __name__ == "__main__":
    app()
