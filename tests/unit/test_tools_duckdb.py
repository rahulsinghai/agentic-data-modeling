"""Unit tests for DuckDB tools."""


from agentic_data_modeling.tools.duckdb_tools import (
    describe_table,
    list_tables,
    load_csv,
    run_query,
)


class TestDuckDBTools:
    def test_run_query(self, duckdb_conn):
        result = run_query.invoke({"sql": "SELECT 1 as num, 'hello' as greeting"})
        assert "num" in result
        assert "hello" in result

    def test_load_csv(self, duckdb_conn, sample_csv):
        result = load_csv.invoke({"file_path": str(sample_csv)})
        assert "50 rows" in result
        assert "orders" in result

    def test_load_csv_missing_file(self, duckdb_conn):
        result = load_csv.invoke({"file_path": "/nonexistent/file.csv"})
        assert "Error" in result

    def test_list_tables(self, duckdb_conn, sample_csv):
        load_csv.invoke({"file_path": str(sample_csv)})
        result = list_tables.invoke({})
        assert "orders" in result

    def test_list_tables_empty(self, duckdb_conn):
        result = list_tables.invoke({})
        assert "No tables" in result

    def test_describe_table(self, duckdb_conn, sample_csv):
        load_csv.invoke({"file_path": str(sample_csv)})
        result = describe_table.invoke({"table_name": "orders"})
        assert "order_id" in result
        assert "customer_id" in result
