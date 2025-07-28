"""Agent state definition for the LangGraph pipeline."""

from __future__ import annotations

import operator
from typing import Annotated

from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    source_dir: str
    output_dir: str
    requirements: str
    next_agent: str
    profiles_json: str
    model_json: str
    dbt_project_json: str
    quality_config_json: str
    artifacts: dict[str, str]
    completed_agents: list[str]
