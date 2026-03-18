"""Modeler sub-agent."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.prompts.modeler import MODELER_SYSTEM_PROMPT
from agentic_data_modeling.tools.modeling_tools import check_grain, validate_star_schema


def _make_llm():
    from langchain_openai import ChatOpenAI

    from agentic_data_modeling.config import get_settings

    settings = get_settings()
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
    )


MODELER_TOOLS = [validate_star_schema, check_grain]


def create_modeler_agent():
    return create_react_agent(
        model=_make_llm(),
        tools=MODELER_TOOLS,
        prompt=MODELER_SYSTEM_PROMPT,
    )


def modeler_node(state: AgentState) -> dict:
    agent = create_modeler_agent()
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        f"Design a dimensional model.\n\n"
                        f"## Source Profiles\n{state.get('profiles_json', 'N/A')}\n\n"
                        f"## Business Requirements\n{state.get('requirements', 'N/A')}"
                    )
                )
            ]
        }
    )
    last_msg = result["messages"][-1]
    return {
        "messages": [last_msg],
        "model_json": last_msg.content,
        "completed_agents": ["modeler"],
    }
