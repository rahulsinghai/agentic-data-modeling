"""Unit tests for codegen tools."""

from agentic_data_modeling.tools.codegen_tools import render_ddl, render_mermaid_erd


class TestCodegenTools:
    def test_render_mermaid_erd(self, sample_dimensional_model):
        result = render_mermaid_erd.invoke(
            {"model_json": sample_dimensional_model.model_dump_json()}
        )
        assert "erDiagram" in result
        assert "dim_customer" in result
        assert "fct_order_items" in result

    def test_render_ddl(self, sample_dimensional_model):
        result = render_ddl.invoke(
            {"model_json": sample_dimensional_model.model_dump_json()}
        )
        assert "CREATE TABLE" in result
        assert "dim_customer" in result

    def test_render_invalid_json(self):
        result = render_mermaid_erd.invoke({"model_json": "not json"})
        assert "Invalid" in result
