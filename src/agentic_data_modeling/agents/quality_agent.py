"""Data quality sub-agent."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.prompts.quality import QUALITY_SYSTEM_PROMPT
from agentic_data_modeling.tools.file_tools import write_artifact
from agentic_data_modeling.tools.quality_tools import render_quality_rules


def _make_llm():
    from langchain_anthropic import ChatAnthropic

    from agentic_data_modeling.config import get_settings

    settings = get_settings()
    return ChatAnthropic(
        model=settings.model,
        api_key=settings.anthropic_api_key,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
    )


QUALITY_TOOLS = [render_quality_rules, write_artifact]


def create_quality_agent():
    return create_react_agent(
        model=_make_llm(),
        tools=QUALITY_TOOLS,
        prompt=QUALITY_SYSTEM_PROMPT,
    )


def quality_node(state: AgentState) -> dict:
    agent = create_quality_agent()
    output_dir = state.get("output_dir", "output")
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        f"Generate data quality rules.\n\n"
                        f"## Dimensional Model\n{state.get('model_json', 'N/A')}\n\n"
                        f"## Source Profiles\n{state.get('profiles_json', 'N/A')}\n\n"
                        f"Output directory: {output_dir}/quality"
                    )
                )
            ]
        }
    )
    last_msg = result["messages"][-1]
    return {
        "messages": [last_msg],
        "quality_config_json": last_msg.content,
        "completed_agents": ["quality_agent"],
    }
