# Agent Graph Details

## State Schema

The pipeline uses `AgentState` (TypedDict) with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| messages | list[AnyMessage] | Conversation history (append-only) |
| source_dir | str | Path to source data files |
| output_dir | str | Path to write artifacts |
| requirements | str | Business requirements text |
| next_agent | str | Router's next-agent decision |
| profiles_json | str | Profiler output |
| model_json | str | Modeler output (DimensionalModel) |
| dbt_project_json | str | dbt generator output |
| quality_config_json | str | Quality agent output |
| artifacts | dict | Map of artifact name → content |
| completed_agents | list[str] | Agents that have finished |

## Routing Logic

The router follows a fixed sequence:
1. profiler → 2. modeler → 3. dbt_generator → 4. doc_generator → 5. quality_agent

Partial runs skip already-completed agents. For example, `adm generate all` pre-marks profiler and modeler as completed.

## Sub-Agent Pattern

Each sub-agent is created with `create_react_agent()` from LangGraph, giving it:
- A ChatAnthropic LLM
- A curated set of tools (no cross-contamination)
- A focused system prompt

The agent node function:
1. Creates a fresh ReAct agent
2. Invokes it with a HumanMessage containing relevant state
3. Extracts the final message content
4. Returns state updates (output JSON + completed_agents marker)
