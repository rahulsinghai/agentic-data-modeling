# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered dimensional data modeling platform using LangGraph with a supervisor pattern. Orchestrates 5 specialized ReAct sub-agents (Profiler, Modeler, DBT Generator, Doc Generator, Quality Agent) via a StateGraph to automate end-to-end data modeling from raw CSV/JSON/Parquet files.

**Stack:** Python 3.13, LangGraph, Pydantic v2, DuckDB (in-memory), Jinja2, Typer+Rich CLI, Streamlit UI, OpenAI/Ollama LLMs.

## Build & Run Commands

```bash
# Setup
pyenv local 3.13.12
uv sync                          # install deps + create .venv

# Run full pipeline
uv run adm run "prompt" --source-dir examples/data/ecommerce --output-dir output/

# Run individual stages
uv run adm profile examples/data/ecommerce
uv run adm model examples/requirements/ecommerce.md --source-dir examples/data/ecommerce
uv run adm generate all output/dimensional_model.json

# Streamlit UI
uv run streamlit run src/agentic_data_modeling/ui/app.py

# Tests
make test                        # unit tests only (no API key needed)
make test-integration            # integration tests (requires OPENAI_API_KEY)
uv run pytest tests/unit/test_models.py -v   # single test file
uv run pytest tests/unit/test_models.py::test_name -v  # single test

# Lint & format
make lint                        # ruff check src/ tests/
make format                      # ruff format src/ tests/
```

## Architecture

### Agent Pipeline

```
START → ROUTER → PROFILER → ROUTER → MODELER → ROUTER → DBT_GENERATOR → ROUTER → DOC_GENERATOR → ROUTER → QUALITY_AGENT → END
```

The Router checks `completed_agents` in state and routes to the next uncompleted agent in sequence. Each agent marks itself done after finishing, then returns to the Router.

### Key Design Patterns

- **LLM decides WHAT, Jinja2 handles HOW**: LLM generates structured JSON (validated via Pydantic), then Jinja2 templates render syntactically correct SQL/YAML/Markdown.
- **Deterministic retries**: Modeler, DBT Generator, and Quality Agent retry up to 2 times on JSON parse or Pydantic validation errors.
- **DuckDB thread safety**: Global lock in `duckdb_tools.py` — always use `with locked_connection() as conn:`.
- **JSON extraction**: LLM responses may include markdown fences; use `_extract_json()` from `tools/modeling_tools.py` to strip them.
- **Model aliases**: `DimensionalModel.facts` accepts both "facts" and "fact_tables" via `AliasChoices`.
- **Temperature = 0.0** for all LLM calls (deterministic).

### State (AgentState TypedDict in `agents/state.py`)

Agents communicate through shared state fields: `messages`, `source_dir`, `output_dir`, `requirements`, `next_agent`, `profiles_json`, `model_json`, `dbt_project_json`, `quality_config_json`, `artifacts`, `completed_agents`.

### Code Layout

- `src/agentic_data_modeling/agents/` — LangGraph StateGraph (`graph.py`), routing (`router.py`), and 5 agent nodes
- `src/agentic_data_modeling/models/` — 6 Pydantic domain models (source profiles, dimensional model, dbt project, quality rules, artifacts)
- `src/agentic_data_modeling/tools/` — 6 tool modules decorated with `@tool` from langchain
- `src/agentic_data_modeling/prompts/` — System prompts per agent
- `src/agentic_data_modeling/renderers/` — Jinja2 engine + 9 templates (dbt SQL, schema YAML, ERD, DDL, docs)
- `src/agentic_data_modeling/cli/` — Typer CLI with 4 commands; `PipelineCallbackHandler` for Rich logging
- `src/agentic_data_modeling/ui/` — Streamlit multi-page app (4 pages + 3 components)

## Configuration

Requires `.env` file (see `.env.example`):
- **OpenAI (default):** `OPENAI_API_KEY`, `ADM_MODEL=gpt-4o-mini`
- **Ollama (local):** `ADM_PROVIDER=ollama`, `ADM_OLLAMA_MODEL=llama3.2`, `ADM_OLLAMA_BASE_URL=http://localhost:11434`

Settings class in `config.py` uses `pydantic-settings` with `ADM_` prefix for env vars.

## Linting

Ruff with rules: E, F, I, N, W, UP. Line length 100. Target Python 3.13. UI page files ignore N999 (module naming).
