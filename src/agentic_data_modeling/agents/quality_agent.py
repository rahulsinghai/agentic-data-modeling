"""Data quality sub-agent.

Asks the LLM to produce a QualityConfig JSON spec, then renders the YAML
template and writes the artifact in Python.
"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.llm import get_llm
from agentic_data_modeling.models.quality import QualityConfig
from agentic_data_modeling.prompts.quality import QUALITY_SYSTEM_PROMPT
from agentic_data_modeling.renderers.engine import render_template
from agentic_data_modeling.tools.quality_tools import _extract_json

logger = logging.getLogger(__name__)


def quality_node(state: AgentState) -> dict:
    llm = get_llm()
    output_dir = state.get("output_dir", "output")
    quality_dir = Path(output_dir) / "quality"
    quality_dir.mkdir(parents=True, exist_ok=True)

    prompt = (
        f"Generate data quality rules.\n\n"
        f"## Dimensional Model\n{state.get('model_json', 'N/A')}\n\n"
        f"## Source Profiles\n{state.get('profiles_json', 'N/A')}\n\n"
        f"Output ONLY valid QualityConfig JSON — no markdown fences, no explanation.\n"
        f"Required structure:\n"
        f'{{"rules": [...], "model_name": "..."}}\n'
        f'Each rule needs: name (str), rule_type ("not_null"|"unique"|"accepted_values"|'
        f'"referential_integrity"|"freshness"|"row_count"|"custom_sql"), '
        f'table (str), column (str or null), severity ("warn"|"error"), description (str).\n\n'
        f"Include:\n"
        f"- not_null on all foreign keys and measures in fact tables\n"
        f"- unique + not_null on dimension primary keys\n"
        f"- referential_integrity for each dimension link\n"
        f"- row_count checks\n"
        f"- accepted_values for categorical columns"
    )

    result = llm.invoke(
        [
            SystemMessage(content=QUALITY_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )
    raw = result.content

    try:
        config = QualityConfig.model_validate_json(_extract_json(raw))
        # Render YAML
        yaml_content = render_template("quality_rules.yml.j2", config=config)
        (quality_dir / "quality_rules.yml").write_text(yaml_content)
        logger.info("Written quality_rules.yml with %d rules", len(config.rules))
        config_json = config.model_dump_json(indent=2)
    except Exception as e:
        logger.warning("QualityConfig validation failed: %s", e)
        config_json = raw

    return {
        "messages": [result],
        "quality_config_json": config_json,
        "completed_agents": ["quality_agent"],
    }
