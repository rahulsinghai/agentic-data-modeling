"""Integration test for CLI commands."""

import pytest
from typer.testing import CliRunner

runner = CliRunner()


@pytest.mark.integration
def test_cli_help():
    from agentic_data_modeling.cli.app import app

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "adm" in result.output.lower() or "agentic" in result.output.lower()
