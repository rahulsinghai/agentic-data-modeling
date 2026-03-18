"""DuckDB tools for loading and querying data."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import duckdb
from langchain_core.tools import tool

# Single in-memory connection shared across the process.
# RLock serializes every execute+fetch block so concurrent tool calls
# (LangGraph runs them in a ThreadPoolExecutor) don't race.
_connection: duckdb.DuckDBPyConnection = duckdb.connect(":memory:")
_lock = threading.RLock()


@contextmanager
def _db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """Acquire the lock and yield the shared connection."""
    with _lock:
        yield _connection


def get_connection() -> duckdb.DuckDBPyConnection:
    return _connection


def set_connection(conn: duckdb.DuckDBPyConnection | None) -> None:
    global _connection
    _connection = conn or duckdb.connect(":memory:")


def reset_connection() -> None:
    """Close current DB and start fresh — call between pipeline runs."""
    global _connection
    with _lock:
        try:
            _connection.close()
        except Exception:
            pass
        _connection = duckdb.connect(":memory:")


@tool
def run_query(sql: str) -> str:
    """Execute a SQL query against DuckDB and return results as formatted text.

    Args:
        sql: SQL query to execute.
    """
    try:
        with _db() as conn:
            result = conn.execute(sql)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
        if not rows:
            return "Query returned 0 rows."
        header = " | ".join(columns)
        separator = "-+-".join("-" * max(len(c), 8) for c in columns)
        lines = [header, separator]
        for row in rows[:100]:
            lines.append(" | ".join(str(v) for v in row))
        if len(rows) > 100:
            lines.append(f"... ({len(rows)} total rows, showing first 100)")
        return "\n".join(lines)
    except Exception as e:
        return f"SQL Error: {e}"


@tool
def load_csv(file_path: str, table_name: str | None = None) -> str:
    """Load a CSV file into DuckDB as a table.

    Args:
        file_path: Path to the CSV file.
        table_name: Optional table name. Defaults to filename stem.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    name = table_name or path.stem
    try:
        with _db() as conn:
            conn.execute(
                f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto('{path}')"
            )
            count = conn.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
        return f"Loaded {count} rows into table '{name}' from {path.name}"
    except Exception as e:
        return f"Error loading CSV: {e}"


@tool
def load_json(file_path: str, table_name: str | None = None) -> str:
    """Load a JSON file into DuckDB as a table.

    Args:
        file_path: Path to the JSON file.
        table_name: Optional table name. Defaults to filename stem.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    name = table_name or path.stem
    try:
        with _db() as conn:
            conn.execute(
                f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_json_auto('{path}')"
            )
            count = conn.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
        return f"Loaded {count} rows into table '{name}' from {path.name}"
    except Exception as e:
        return f"Error loading JSON: {e}"


@tool
def list_tables() -> str:
    """List all tables currently loaded in DuckDB."""
    with _db() as conn:
        tables = conn.execute("SHOW TABLES").fetchall()
    if not tables:
        return "No tables loaded."
    return "\n".join(f"- {t[0]}" for t in tables)


@tool
def describe_table(table_name: str) -> str:
    """Show column names, types, and nullable info for a table.

    Args:
        table_name: Name of the table to describe.
    """
    try:
        with _db() as conn:
            cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
        lines = [f"{'Column':<30} {'Type':<20} {'Null':<6}"]
        lines.append("-" * 56)
        for col in cols:
            lines.append(f"{col[0]:<30} {col[1]:<20} {col[2]:<6}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"
