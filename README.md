# Agentic Data Modeling

AI agents that automate dimensional data modeling end-to-end.
LLM-powered agents profile source data, design star/snowflake schemas, generate dbt models, ERDs, DDL, data quality rules, and documentation; all orchestrated via LangGraph.

## Architecture

```
              ┌───────────┐
   START ───▶ │  ROUTER   │◀──────────────────────────┐
              └─────┬─────┘                           │
        ┌───────┬───┴───┬─────────┐                   │
        ▼       ▼       ▼         ▼                   │
   PROFILER  MODELER  DBT_GEN  DOC_GEN                │
        │       │       │         │                   │
        └───────┴───┬───┴─────────┘                   │
                    ▼                                 │
              QUALITY_AGENT ──────────────────────────┘
                    │
                   END
```

5 specialized ReAct sub-agents, each with curated tools, coordinated by a supervisor router. LLM decides **what** to generate; Jinja2 templates handle **how**; deterministic, correct syntax every time.

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv); manages the Python version
- [uv](https://docs.astral.sh/uv/); manages dependencies and virtual environment

## Quick Start

### 1. Install Python 3.13.12 via pyenv

```bash
# Install pyenv (macOS)
brew install pyenv

# Add to shell (bash/zsh)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install Python 3.13.12 (pinned in .python-version)
pyenv install --list
pyenv install 3.13.12

pyenv local 3.13.12

# Confirm; should print 3.13.12
python --version
```

> The `.python-version` file at the repo root automatically activates Python 3.13.12
> whenever you `cd` into this directory.

### 2. Install dependencies

```bash
# uv respects .python-version and creates .venv automatically
uv sync
```

### 3. Configure API key

```bash
cp .env.example .env
# Edit .env; set OPENAI_API_KEY=sk-...
```

### 4. Run

```bash
# Full pipeline
uv run adm run "Analyze ecommerce sales" \
  --source-dir examples/data/ecommerce \
  --output-dir output/

# Individual steps
uv run adm profile examples/data/ecommerce
uv run adm model examples/requirements/ecommerce.md --source-dir examples/data/ecommerce
uv run adm generate all output/dimensional_model.json
uv run adm generate erd output/dimensional_model.json
uv run adm generate ddl output/dimensional_model.json
```

## Streamlit UI

```bash
uv run streamlit run src/agentic_data_modeling/ui/app.py
```

Upload CSVs, enter business requirements, and generate all artifacts interactively.

## Tech Stack

| Component     | Technology                                 |
|---------------|--------------------------------------------|
| Python        | 3.13.12 (pinned via `.python-version`)     |
| Orchestration | LangGraph (StateGraph + conditional edges) |
| LLM           | OpenAI GPT-4o-mini via langchain-openai    |
| Data Engine   | DuckDB (in-memory)                         |
| Domain Models | Pydantic v2                                |
| Templates     | Jinja2                                     |
| CLI           | Typer + Rich                               |
| UI            | Streamlit                                  |

## Project Structure

```
src/agentic_data_modeling/
├── config.py              # Pydantic Settings
├── models/                # Domain models (source, dimensional, dbt, quality, artifacts)
├── tools/                 # @tool functions (DuckDB, profiling, codegen, quality, file I/O)
├── agents/                # LangGraph graph + sub-agents (profiler, modeler, dbt, docs, quality)
├── prompts/               # System prompts per agent
├── renderers/             # Jinja2 templates + engine
├── cli/                   # Typer CLI commands
└── ui/                    # Streamlit app with 4 pages
```

## Testing

```bash
# Unit tests (no API key needed)
make test

# Integration tests (requires ANTHROPIC_API_KEY)
make test-integration

# Lint
make lint
```

## Sample Datasets

- **ecommerce/**; customers, products, categories, orders, order_items (~200 customers, ~1000 orders)
- **saas_events/**; users, subscriptions, events (~150 users, ~2000 events)

## Generated Artifacts

The pipeline produces:
- **Source profiles**; column stats, PK/FK detection, grain inference
- **Dimensional model**; facts, dimensions, measures, grain, SCD types
- **dbt models**; staging, intermediate, mart SQL + schema.yml + sources.yml
- **ERD**; Mermaid entity-relationship diagram
- **DDL**; CREATE TABLE statements (DuckDB dialect)
- **Quality rules**; not-null, unique, referential integrity, freshness checks
- **Documentation**; comprehensive markdown docs

## License

MIT
