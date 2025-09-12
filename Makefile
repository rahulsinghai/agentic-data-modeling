.PHONY: test test-unit test-integration lint format ui run clean

test: test-unit

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v -m integration

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

ui:
	uv run streamlit run src/agentic_data_modeling/ui/app.py

run:
	uv run adm run "Analyze ecommerce sales" --source-dir examples/data/ecommerce --output-dir output/

clean:
	rm -rf output/ .pytest_cache/ __pycache__/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
