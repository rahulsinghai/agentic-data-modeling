"""dbt code generation sub-agent."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.prompts.dbt_generator import DBT_GENERATOR_SYSTEM_PROMPT
from agentic_data_modeling.tools.codegen_tools import (
    render_dbt_model,
    render_dbt_schema,
    render_dbt_sources,
)
from agentic_data_modeling.tools.file_tools import write_artifact


def _make_llm():
    from langchain_openai import ChatOpenAI

    from agentic_data_modeling.config import get_settings

    settings = get_settings()
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
    )


DBT_GEN_TOOLS = [render_dbt_model, render_dbt_schema, render_dbt_sources, write_artifact]


def create_dbt_generator_agent():
    return create_react_agent(
        model=_make_llm(),
        tools=DBT_GEN_TOOLS,
        prompt=DBT_GENERATOR_SYSTEM_PROMPT,
    )


def dbt_generator_node(state: AgentState) -> dict:
    agent = create_dbt_generator_agent()
    output_dir = state.get("output_dir", "output")
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        f"Generate dbt models for this dimensional model.\n\n"
                        f"## Dimensional Model\n{state.get('model_json', 'N/A')}\n\n"
                        f"Output directory: {output_dir}/dbt"
                    )
                )
            ]
        }
    )
    last_msg = result["messages"][-1]
    return {
        "messages": [last_msg],
        "dbt_project_json": last_msg.content,
        "completed_agents": ["dbt_generator"],
    }
