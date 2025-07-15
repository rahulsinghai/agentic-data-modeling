"""Code generation tools using Jinja2 templates."""

from __future__ import annotations

from langchain_core.tools import tool

from agentic_data_modeling.models.artifacts import DDLStatement, ERDiagram
from agentic_data_modeling.models.dbt import DbtModel, DbtProject, DbtSource
from agentic_data_modeling.models.dimensional import DimensionalModel
from agentic_data_modeling.renderers.engine import render_template


@tool
def render_dbt_model(model_json: str) -> str:
    """Render a dbt SQL model from a DbtModel JSON spec.

    Args:
        model_json: JSON string of DbtModel.
    """
    try:
        model = DbtModel.model_validate_json(model_json)
    except Exception as e:
        return f"Invalid DbtModel JSON: {e}"
    template_name = f"dbt_{model.model_type.value}.sql.j2"
    return render_template(template_name, model=model)


@tool
def render_dbt_schema(project_json: str) -> str:
    """Render a dbt schema.yml from a DbtProject JSON spec.

    Args:
        project_json: JSON string of DbtProject.
    """
    try:
        project = DbtProject.model_validate_json(project_json)
    except Exception as e:
        return f"Invalid DbtProject JSON: {e}"
    return render_template("dbt_schema.yml.j2", project=project)


@tool
def render_dbt_sources(source_json: str) -> str:
    """Render a dbt sources.yml from a DbtSource JSON spec.

    Args:
        source_json: JSON string of DbtSource.
    """
    try:
        source = DbtSource.model_validate_json(source_json)
    except Exception as e:
        return f"Invalid DbtSource JSON: {e}"
    return render_template("dbt_sources.yml.j2", source=source)


@tool
def render_ddl(model_json: str) -> str:
    """Render DDL statements from a DimensionalModel JSON spec.

    Args:
        model_json: JSON string of DimensionalModel.
    """
    try:
        model = DimensionalModel.model_validate_json(model_json)
    except Exception as e:
        return f"Invalid DimensionalModel JSON: {e}"

    statements: list[DDLStatement] = []
    for dim in model.dimensions:
        ddl = render_template("ddl_duckdb.sql.j2", table=dim, table_type="dimension")
        statements.append(DDLStatement(table_name=dim.name, ddl=ddl))
    for fact in model.facts:
        ddl = render_template("ddl_duckdb.sql.j2", table=fact, table_type="fact")
        statements.append(DDLStatement(table_name=fact.name, ddl=ddl))

    return "\n\n".join(s.ddl for s in statements)


@tool
def render_mermaid_erd(model_json: str) -> str:
    """Render a Mermaid ERD diagram from a DimensionalModel JSON spec.

    Args:
        model_json: JSON string of DimensionalModel.
    """
    try:
        model = DimensionalModel.model_validate_json(model_json)
    except Exception as e:
        return f"Invalid DimensionalModel JSON: {e}"

    erd = ERDiagram(
        title=model.name,
        mermaid_code=render_template("erd_mermaid.md.j2", model=model),
    )
    return erd.mermaid_code
