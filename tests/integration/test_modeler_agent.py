"""Integration test for the modeler agent."""

import pytest


@pytest.mark.integration
def test_modeler_agent():
    """Test that the modeler agent can design a dimensional model."""
    from agentic_data_modeling.agents.modeler import modeler_node

    requirements = (
        "Design a star schema for e-commerce "
        "with customers, products, and orders."
    )
    profiles = (
        '{"tables": [{"name": "orders", '
        '"columns": ["order_id", "customer_id", "amount"]}]}'
    )
    result = modeler_node(
        {
            "messages": [],
            "source_dir": "",
            "output_dir": "/tmp/adm_test_output",
            "requirements": requirements,
            "next_agent": "",
            "profiles_json": profiles,
            "model_json": "",
            "dbt_project_json": "",
            "quality_config_json": "",
            "artifacts": {},
            "completed_agents": [],
        }
    )
    assert "model_json" in result
    assert result["model_json"]
