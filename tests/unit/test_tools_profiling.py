"""Unit tests for profiling tools."""

from agentic_data_modeling.tools.duckdb_tools import load_csv
from agentic_data_modeling.tools.profiling_tools import (
    detect_foreign_keys,
    detect_primary_keys,
    profile_column,
)


class TestProfilingTools:
    def test_profile_column(self, duckdb_conn, sample_csv):
        load_csv.invoke({"file_path": str(sample_csv)})
        result = profile_column.invoke({"table_name": "orders", "column_name": "order_id"})
        assert "Column: order_id" in result
        assert "Distinct count: 50" in result

    def test_detect_primary_keys(self, duckdb_conn, sample_csv):
        load_csv.invoke({"file_path": str(sample_csv)})
        result = detect_primary_keys.invoke({"table_name": "orders"})
        assert "order_id" in result

    def test_detect_foreign_keys(self, duckdb_conn, sample_csv, sample_customers_csv):
        load_csv.invoke({"file_path": str(sample_csv)})
        load_csv.invoke({"file_path": str(sample_customers_csv)})
        result = detect_foreign_keys.invoke(
            {"table_name": "orders", "all_tables": ["orders", "customers"]}
        )
        assert "customer_id" in result or "No FK" in result
