"""Documentation generation sub-agent.

Renders ERD, DDL, and documentation from the dimensional model in Python.
Uses the LLM only to generate the prose documentation.
"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.llm import get_llm
from agentic_data_modeling.models.dimensional import DimensionalModel
from agentic_data_modeling.renderers.engine import render_template
from agentic_data_modeling.tools.codegen_tools import _extract_json

logger = logging.getLogger(__name__)


def doc_generator_node(state: AgentState) -> dict:
    output_dir = state.get("output_dir", "output")
    docs_dir = Path(output_dir) / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    model_json = state.get("model_json", "")

    # Parse the dimensional model
    try:
        model = DimensionalModel.model_validate_json(_extract_json(model_json))
    except Exception as e:
        logger.error("Failed to parse DimensionalModel: %s", e)
        from langchain_core.messages import AIMessage

        msg = AIMessage(content=f"Error parsing model: {e}")
        return {
            "messages": [msg],
            "completed_agents": ["doc_generator"],
        }

    # Render ERD
    try:
        erd_code = render_template("erd_mermaid.md.j2", model=model)
        (docs_dir / "erd.md").write_text(erd_code)
        logger.info("Written erd.md")
    except Exception as e:
        logger.warning("Failed to render ERD: %s", e)

    # Render DDL
    try:
        ddl_parts = []
        for dim in model.dimensions:
            ddl_parts.append(
                render_template("ddl_duckdb.sql.j2", table=dim, table_type="dimension")
            )
        for fact in model.facts:
            ddl_parts.append(render_template("ddl_duckdb.sql.j2", table=fact, table_type="fact"))
        ddl_text = "\n\n".join(ddl_parts)
        (docs_dir / "ddl.sql").write_text(ddl_text)
        logger.info("Written ddl.sql")
    except Exception as e:
        logger.warning("Failed to render DDL: %s", e)

    # Ask LLM to generate prose documentation
    llm = get_llm()
    doc_prompt = (
        f"Write comprehensive model documentation in Markdown for the following "
        f"dimensional model. Cover: overview, fact tables (with grain and measures), "
        f"dimension tables (with attributes and SCD types), relationships, and "
        f"any data quality considerations.\n\n"
        f"## Dimensional Model\n{model_json}\n\n"
        f"## Business Requirements\n{state.get('requirements', 'N/A')}\n\n"
        f"Output ONLY Markdown documentation."
    )
    result = llm.invoke(
        [
            SystemMessage(
                content="You are a documentation writer. Produce clear, comprehensive "
                "Markdown documentation for data models."
            ),
            HumanMessage(content=doc_prompt),
        ]
    )

    try:
        (docs_dir / "documentation.md").write_text(result.content)
        logger.info("Written documentation.md")
    except Exception as e:
        logger.warning("Failed to write documentation: %s", e)

    return {
        "messages": [result],
        "completed_agents": ["doc_generator"],
    }
