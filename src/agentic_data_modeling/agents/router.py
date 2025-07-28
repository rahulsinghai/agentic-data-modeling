"""Supervisor router node."""

from __future__ import annotations

from agentic_data_modeling.agents.state import AgentState

AGENT_SEQUENCE = ["profiler", "modeler", "dbt_generator", "doc_generator", "quality_agent"]


def router_node(state: AgentState) -> dict:
    """Decide which agent to run next based on completed agents."""
    completed = state.get("completed_agents", [])
    for agent in AGENT_SEQUENCE:
        if agent not in completed:
            return {"next_agent": agent}
    return {"next_agent": "END"}


def route_next(state: AgentState) -> str:
    """Conditional edge function: returns the next node name or END."""
    next_agent = state.get("next_agent", "END")
    if next_agent == "END":
        return "__end__"
    return next_agent
