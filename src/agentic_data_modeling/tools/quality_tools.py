"""Data quality rule generation tools."""

from __future__ import annotations

import json
import re

from langchain_core.tools import tool

from agentic_data_modeling.models.quality import QualityConfig
from agentic_data_modeling.renderers.engine import render_template


def _extract_json(text) -> str:
    """Normalize input to a JSON string. Accepts str or dict/list."""
    if isinstance(text, (dict, list)):
        return json.dumps(text)
    text = text.strip()
    text = re.sub(r"^```(?:json)?[ \t]*\n?", "", text).strip()
    start = next((i for i, c in enumerate(text) if c in "{["), 0)
    text = text[start:]
    try:
        obj, _ = json.JSONDecoder().raw_decode(text)
        return json.dumps(obj)
    except json.JSONDecodeError:
        return text


@tool
def render_quality_rules(config_json: str | dict) -> str:
    """Render quality rules as YAML from a QualityConfig JSON spec.

    Args:
        config_json: JSON string or dict of QualityConfig.
    """
    try:
        config = QualityConfig.model_validate_json(_extract_json(config_json))
    except Exception as e:
        return f"Invalid QualityConfig JSON: {e}"
    return render_template("quality_rules.yml.j2", config=config)
