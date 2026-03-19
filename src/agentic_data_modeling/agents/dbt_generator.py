"""dbt code generation sub-agent.

Asks the LLM to produce a DbtProject JSON spec, then renders all templates
and writes artifacts in Python.
"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.llm import get_llm
from agentic_data_modeling.models.dbt import DbtProject
from agentic_data_modeling.prompts.dbt_generator import DBT_GENERATOR_SYSTEM_PROMPT
from agentic_data_modeling.renderers.engine import render_template
from agentic_data_modeling.tools.codegen_tools import _extract_json

logger = logging.getLogger(__name__)


def _render_and_write(output_dir: str, project: DbtProject) -> list[str]:
    """Render all dbt artifacts and write them to disk. Returns list of files written."""
    dbt_dir = Path(output_dir) / "dbt"
    dbt_dir.mkdir(parents=True, exist_ok=True)
    written = []

    # Render SQL models
    for model in project.models:
        template_name = f"dbt_{model.model_type.value}.sql.j2"
        try:
            sql = render_template(template_name, model=model)
            path = dbt_dir / f"{model.name}.sql"
            path.write_text(sql)
            written.append(str(path))
        except Exception as e:
            logger.warning("Failed to render model %s: %s", model.name, e)

    # Render schema.yml
    try:
        schema = render_template("dbt_schema.yml.j2", project=project)
        path = dbt_dir / "schema.yml"
        path.write_text(schema)
        written.append(str(path))
    except Exception as e:
        logger.warning("Failed to render schema.yml: %s", e)

    # Render sources.yml for each source
    for source in project.sources:
        try:
            sources_yml = render_template("dbt_sources.yml.j2", source=source)
            path = dbt_dir / "sources.yml"
            path.write_text(sources_yml)
            written.append(str(path))
        except Exception as e:
            logger.warning("Failed to render sources.yml: %s", e)

    return written


def dbt_generator_node(state: AgentState) -> dict:
    llm = get_llm()
    output_dir = state.get("output_dir", "output")

    prompt = (
        f"Generate a dbt project specification for this dimensional model.\n\n"
        f"## Dimensional Model\n{state.get('model_json', 'N/A')}\n\n"
        f"Output ONLY valid DbtProject JSON — no markdown fences, no explanation.\n"
        f"Required structure:\n"
        f'{{"name": "...", "sources": [...], "models": [...]}}\n\n'
        f"Each source needs: name (str), tables (list of table name strings), schema_name (str).\n"
        f'Each model needs: name (str), model_type ("staging"|"intermediate"|"mart"), '
        f'materialization ("view"|"table"), description (str), '
        f"sql (str with the SELECT statement), "
        f"columns (list of {{name, description, data_type, tests}}), "
        f"depends_on (list of model names).\n\n"
        f"## Conventions\n"
        f"- Staging: stg_<source>__<table>.sql; rename, cast, minimal transforms\n"
        f"- Mart: dim_<name>.sql / fct_<name>.sql; final star schema tables\n"
        f"- Include not_null/unique tests on key columns"
    )

    result = llm.invoke(
        [
            SystemMessage(content=DBT_GENERATOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )
    raw = result.content

    try:
        project = DbtProject.model_validate_json(_extract_json(raw))
        written = _render_and_write(output_dir, project)
        logger.info("dbt artifacts written: %s", written)
        project_json = project.model_dump_json(indent=2)
    except Exception as e:
        logger.warning("DbtProject validation failed: %s", e)
        project_json = raw

    return {
        "messages": [result],
        "dbt_project_json": project_json,
        "completed_agents": ["dbt_generator"],
    }
