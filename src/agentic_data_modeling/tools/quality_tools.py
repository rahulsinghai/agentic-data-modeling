"""Data quality rule generation tools."""

from __future__ import annotations

from langchain_core.tools import tool

from agentic_data_modeling.models.quality import QualityConfig
from agentic_data_modeling.renderers.engine import render_template


@tool
def render_quality_rules(config_json: str) -> str:
    """Render quality rules as YAML from a QualityConfig JSON spec.

    Args:
        config_json: JSON string of QualityConfig.
    """
    try:
        config = QualityConfig.model_validate_json(config_json)
    except Exception as e:
        return f"Invalid QualityConfig JSON: {e}"
    return render_template("quality_rules.yml.j2", config=config)
