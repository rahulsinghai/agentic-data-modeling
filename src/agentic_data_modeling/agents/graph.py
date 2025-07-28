"""LangGraph pipeline assembly."""

from __future__ import annotations

from langgraph.graph import StateGraph

from agentic_data_modeling.agents.dbt_generator import dbt_generator_node
from agentic_data_modeling.agents.doc_generator import doc_generator_node
from agentic_data_modeling.agents.modeler import modeler_node
from agentic_data_modeling.agents.profiler import profiler_node
from agentic_data_modeling.agents.quality_agent import quality_node
from agentic_data_modeling.agents.router import route_next, router_node
from agentic_data_modeling.agents.state import AgentState


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("profiler", profiler_node)
    graph.add_node("modeler", modeler_node)
    graph.add_node("dbt_generator", dbt_generator_node)
    graph.add_node("doc_generator", doc_generator_node)
    graph.add_node("quality_agent", quality_node)

    # Entry point
    graph.set_entry_point("router")

    # Router decides next agent
    graph.add_conditional_edges(
        "router",
        route_next,
        {
            "profiler": "profiler",
            "modeler": "modeler",
            "dbt_generator": "dbt_generator",
            "doc_generator": "doc_generator",
            "quality_agent": "quality_agent",
            "__end__": "__end__",
        },
    )

    # Each agent returns to router
    for agent_name in ["profiler", "modeler", "dbt_generator", "doc_generator", "quality_agent"]:
        graph.add_edge(agent_name, "router")

    return graph


def compile_graph():
    return build_graph().compile()
