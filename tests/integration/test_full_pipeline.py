"""Integration test for the full pipeline."""

import pytest


@pytest.mark.integration
def test_full_pipeline(sample_csv, sample_customers_csv, tmp_path):
    """Test running the full pipeline end-to-end."""
    from agentic_data_modeling.agents.graph import compile_graph

    graph = compile_graph()
    result = graph.invoke(
        {
            "messages": [],
            "source_dir": str(sample_csv.parent),
            "output_dir": str(tmp_path / "output"),
            "requirements": "Analyze order patterns and customer segments.",
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
    assert result.get("profiles_json")
    assert result.get("model_json")
    assert "quality_agent" in result.get("completed_agents", [])
