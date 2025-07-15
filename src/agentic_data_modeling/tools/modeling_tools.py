"""Validation tools for dimensional models."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from agentic_data_modeling.models.dimensional import DimensionalModel


@tool
def validate_star_schema(model_json: str) -> str:
    """Validate a dimensional model for completeness and consistency.

    Args:
        model_json: JSON string of the DimensionalModel.
    """
    try:
        model = DimensionalModel.model_validate_json(model_json)
    except Exception as e:
        return f"Invalid model JSON: {e}"

    issues: list[str] = []

    if not model.facts:
        issues.append("Model has no fact tables.")
    if not model.dimensions:
        issues.append("Model has no dimensions.")

    dim_names = {d.name for d in model.dimensions}
    for fact in model.facts:
        if not fact.grain:
            issues.append(f"Fact '{fact.name}' has no grain defined.")
        if not fact.measures:
            issues.append(f"Fact '{fact.name}' has no measures.")
        for link in fact.dimension_links:
            if link.dimension_name not in dim_names:
                issues.append(
                    f"Fact '{fact.name}' references unknown dimension '{link.dimension_name}'."
                )

    for dim in model.dimensions:
        if not dim.primary_key:
            issues.append(f"Dimension '{dim.name}' has no primary key.")
        if not dim.attributes:
            issues.append(f"Dimension '{dim.name}' has no attributes.")

    if issues:
        return "Validation issues:\n" + "\n".join(f"  - {i}" for i in issues)
    return "Model is valid."


@tool
def check_grain(fact_name: str, grain: str, dimension_links: str) -> str:
    """Check that a fact table's grain is consistent with its dimension links.

    Args:
        fact_name: Name of the fact table.
        grain: Description of the grain (e.g., "one row per order line item").
        dimension_links: JSON list of dimension link names.
    """
    try:
        links = json.loads(dimension_links)
    except Exception:
        return "Error: dimension_links must be a JSON list of strings."

    if not grain:
        return f"Fact '{fact_name}' has no grain defined."

    return (
        f"Grain check for '{fact_name}':\n"
        f"  Grain: {grain}\n"
        f"  Linked dimensions: {', '.join(links)}\n"
        f"  Status: Grain defined with {len(links)} dimension links. "
        f"Verify that the grain matches the combination of dimension keys."
    )
