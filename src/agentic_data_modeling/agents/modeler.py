"""Modeler sub-agent.

Asks the LLM to produce a DimensionalModel JSON spec, validates it in Python,
and runs grain checks deterministically.
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.llm import get_llm
from agentic_data_modeling.models.dimensional import DimensionalModel
from agentic_data_modeling.prompts.modeler import MODELER_SYSTEM_PROMPT
from agentic_data_modeling.tools.modeling_tools import _extract_json

logger = logging.getLogger(__name__)

_MAX_RETRIES = 2


def modeler_node(state: AgentState) -> dict:
    llm = get_llm()

    prompt = (
        f"Design a dimensional model.\n\n"
        f"## Source Profiles\n{state.get('profiles_json', 'N/A')}\n\n"
        f"## Business Requirements\n{state.get('requirements', 'N/A')}\n\n"
        f"Output ONLY valid DimensionalModel JSON — no markdown fences, no explanation.\n"
        f'Required structure: {{"name": "...", "facts": [...], "dimensions": [...]}}\n'
        f"Each fact needs: name, grain, measures (list of {{name, data_type, aggregation}}), "
        f"dimension_links (list of {{dimension_name, foreign_key}}).\n"
        f"Each dimension needs: name, primary_key, attributes (list of {{name, data_type}})."
    )

    last_error = None
    for attempt in range(_MAX_RETRIES + 1):
        messages = [
            SystemMessage(content=MODELER_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        if last_error:
            messages.append(
                HumanMessage(
                    content=f"Your previous output had a validation error: {last_error}\n"
                    f"Please fix the JSON and try again. Output ONLY valid JSON."
                )
            )

        result = llm.invoke(messages)
        raw = result.content

        try:
            model = DimensionalModel.model_validate_json(_extract_json(raw))

            # Run grain checks in Python
            issues = []
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
                            f"Fact '{fact.name}' references unknown dimension "
                            f"'{link.dimension_name}'."
                        )
            for dim in model.dimensions:
                if not dim.primary_key:
                    issues.append(f"Dimension '{dim.name}' has no primary key.")
                if not dim.attributes:
                    issues.append(f"Dimension '{dim.name}' has no attributes.")

            if issues:
                logger.warning("Model validation issues: %s", issues)
                last_error = "; ".join(issues)
                if attempt < _MAX_RETRIES:
                    continue

            # Serialize the validated model back to JSON for downstream agents
            model_json = model.model_dump_json(indent=2)
            logger.info("Dimensional model validated: %s", model.name)
            return {
                "messages": [result],
                "model_json": model_json,
                "completed_agents": ["modeler"],
            }
        except Exception as e:
            last_error = str(e)
            logger.warning("Model validation attempt %d failed: %s", attempt + 1, e)
            if attempt < _MAX_RETRIES:
                continue

    # Return best-effort even if validation failed
    return {
        "messages": [result],
        "model_json": raw,
        "completed_agents": ["modeler"],
    }
