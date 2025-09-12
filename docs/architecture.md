# Architecture

## Overview

Agentic Data Modeling uses a LangGraph supervisor pattern where a router node delegates to 5 specialized ReAct sub-agents.

## Agent Pipeline

```
              ┌──────────┐
   START ───▶ │  ROUTER   │◀─────────────────────────┐
              └─────┬─────┘                           │
        ┌───────┬───┴───┬─────────┐                   │
        ▼       ▼       ▼         ▼                   │
   PROFILER  MODELER  DBT_GEN  DOC_GEN                │
        │       │       │         │                   │
        └───────┴───┬───┴─────────┘                   │
                    ▼                                  │
              QUALITY_AGENT ──────────────────────────┘
                    │
                   END
```

## Sub-Agents

| Agent | Purpose | Tools |
|-------|---------|-------|
| Profiler | Load data, profile columns, detect keys | DuckDB tools, profiling tools |
| Modeler | Design star/snowflake schema | Validation tools |
| dbt Generator | Produce dbt SQL models + schema.yml | Codegen tools, file tools |
| Doc Generator | Render ERD, DDL, documentation | Codegen tools, file tools |
| Quality Agent | Generate data quality rules | Quality tools, file tools |

## Key Design Decision

LLM decides **what** to generate (via structured Pydantic outputs). Jinja2 templates handle **how** to format it. This ensures deterministic, syntactically correct output every time.

## Tech Stack

- **Orchestration:** LangGraph StateGraph with conditional edges
- **LLM:** Claude (via langchain-anthropic)
- **Data:** DuckDB (in-memory)
- **Models:** Pydantic v2
- **Templates:** Jinja2
- **CLI:** Typer + Rich
- **UI:** Streamlit
