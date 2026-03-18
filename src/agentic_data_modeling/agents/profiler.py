"""Profiler sub-agent."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.config import get_settings
from agentic_data_modeling.prompts.profiler import PROFILER_SYSTEM_PROMPT
from agentic_data_modeling.tools.duckdb_tools import (
    describe_table,
    list_tables,
    load_csv,
    load_json,
    run_query,
)
from agentic_data_modeling.tools.file_tools import list_directory
from agentic_data_modeling.tools.profiling_tools import (
    detect_foreign_keys,
    detect_primary_keys,
    profile_column,
)


def _make_llm():
    from langchain_openai import ChatOpenAI

    settings = get_settings()
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
    )


PROFILER_TOOLS = [
    load_csv,
    load_json,
    list_tables,
    describe_table,
    run_query,
    profile_column,
    detect_primary_keys,
    detect_foreign_keys,
    list_directory,
]


def create_profiler_agent():
    return create_react_agent(
        model=_make_llm(),
        tools=PROFILER_TOOLS,
        prompt=PROFILER_SYSTEM_PROMPT,
    )


def profiler_node(state: AgentState) -> dict:
    agent = create_profiler_agent()
    source_dir = state.get("source_dir", "")
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=f"Profile all data files in: {source_dir}\n"
                    f"Requirements context: {state.get('requirements', 'N/A')}"
                )
            ]
        }
    )
    last_msg = result["messages"][-1]
    return {
        "messages": [last_msg],
        "profiles_json": last_msg.content,
        "completed_agents": ["profiler"],
    }
