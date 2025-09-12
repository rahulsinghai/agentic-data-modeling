"""Integration test for the profiler agent."""

import pytest


@pytest.mark.integration
def test_profiler_agent(sample_csv, sample_customers_csv):
    """Test that the profiler agent can load and profile data."""
    from agentic_data_modeling.agents.profiler import profiler_node

    result = profiler_node(
        {
            "messages": [],
            "source_dir": str(sample_csv.parent),
            "output_dir": "/tmp/adm_test_output",
            "requirements": "Analyze order data",
            "next_agent": "",
            "profiles_json": "",
            "model_json": "",
            "dbt_project_json": "",
            "quality_config_json": "",
            "artifacts": {},
            "completed_agents": [],
        }
    )
    assert "profiles_json" in result
    assert result["profiles_json"]
