"""SQL-based column profiling and key detection tools."""

from __future__ import annotations

from langchain_core.tools import tool

from agentic_data_modeling.tools.duckdb_tools import locked_connection


@tool
def profile_column(table_name: str, column_name: str) -> str:
    """Profile a single column: type, nulls, distinct count, min/max, samples.

    Args:
        table_name: Table to profile.
        column_name: Column to profile.
    """
    try:
        with locked_connection() as conn:
            # Get type separately (typeof is not an aggregate)
            type_row = conn.execute(
                f'SELECT typeof("{column_name}") FROM {table_name} LIMIT 1'
            ).fetchone()
            data_type = type_row[0] if type_row else "UNKNOWN"

            sql = f"""
            SELECT
                count(*) as total,
                count("{column_name}") as non_null,
                count(*) - count("{column_name}") as null_count,
                count(DISTINCT "{column_name}") as distinct_count,
                min("{column_name}")::varchar as min_val,
                max("{column_name}")::varchar as max_val
            FROM {table_name}
            """
            row = conn.execute(sql).fetchone()

            # Get sample values
            sample_sql = f"""
            SELECT DISTINCT "{column_name}"::varchar as val
            FROM {table_name}
            WHERE "{column_name}" IS NOT NULL
            LIMIT 5
            """
            samples = [r[0] for r in conn.execute(sample_sql).fetchall()]

            # Try mean for numeric
            mean_str = "N/A"
            try:
                mean_row = conn.execute(
                    f'SELECT avg("{column_name}")::float as m FROM {table_name}'
                ).fetchone()
                if mean_row and mean_row[0] is not None:
                    mean_str = f"{mean_row[0]:.4f}"
            except Exception:
                pass

        return (
            f"Column: {column_name}\n"
            f"Type: {data_type}\n"
            f"Total rows: {row[0]}\n"
            f"Non-null: {row[1]}\n"
            f"Null count: {row[2]}\n"
            f"Distinct count: {row[3]}\n"
            f"Min: {row[4]}\n"
            f"Max: {row[5]}\n"
            f"Mean: {mean_str}\n"
            f"Samples: {samples}"
        )
    except Exception as e:
        return f"Error profiling {column_name}: {e}"


@tool
def detect_primary_keys(table_name: str) -> str:
    """Detect candidate primary keys by checking uniqueness and non-null.

    Args:
        table_name: Table to analyze.
    """
    try:
        with locked_connection() as conn:
            cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
            total = conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]
            candidates = []
            for col in cols:
                col_name = col[0]
                sql = f"""
                SELECT
                    count(DISTINCT "{col_name}") as dist,
                    count(*) - count("{col_name}") as nulls
                FROM {table_name}
                """
                row = conn.execute(sql).fetchone()
                if row[0] == total and row[1] == 0:
                    candidates.append(col_name)
        if not candidates:
            return f"No single-column PK candidates found for {table_name} ({total} rows)."
        return f"PK candidates for {table_name}: {', '.join(candidates)}"
    except Exception as e:
        return f"Error: {e}"


@tool
def detect_foreign_keys(table_name: str, all_tables: list[str]) -> str:
    """Detect potential foreign key relationships by matching column values.

    Args:
        table_name: Source table to check FK columns in.
        all_tables: List of all table names to check references against.
    """
    try:
        with locked_connection() as conn:
            source_col_rows = conn.execute(f"DESCRIBE {table_name}").fetchall()
            # Build {col_name: type} map for source table
            source_types = {r[0]: r[1] for r in source_col_rows}
            fk_candidates = []

            for col_name, col_type in source_types.items():
                # Only check columns ending in _id or _key
                if not (col_name.endswith("_id") or col_name.endswith("_key")):
                    continue

                for ref_table in all_tables:
                    if ref_table == table_name:
                        continue
                    ref_cols = conn.execute(f"DESCRIBE {ref_table}").fetchall()
                    ref_total = conn.execute(f"SELECT count(*) FROM {ref_table}").fetchone()[0]

                    for ref_col in ref_cols:
                        ref_col_name, ref_col_type = ref_col[0], ref_col[1]
                        # Skip type mismatches to avoid cast errors in EXCEPT
                        if ref_col_type != col_type:
                            continue
                        ref_dist = conn.execute(
                            f'SELECT count(DISTINCT "{ref_col_name}") FROM {ref_table}'
                        ).fetchone()[0]
                        if ref_dist != ref_total:
                            continue

                        # Check containment (same types guaranteed above)
                        sql = f"""
                        SELECT count(*) FROM (
                            SELECT DISTINCT "{col_name}" FROM {table_name}
                            WHERE "{col_name}" IS NOT NULL
                            EXCEPT
                            SELECT DISTINCT "{ref_col_name}" FROM {ref_table}
                        )
                        """
                        orphans = conn.execute(sql).fetchone()[0]
                        if orphans == 0:
                            fk_candidates.append(
                                f"{table_name}.{col_name} -> {ref_table}.{ref_col_name}"
                            )

        if not fk_candidates:
            return f"No FK candidates found for {table_name}."
        return "FK candidates:\n" + "\n".join(f"  {fk}" for fk in fk_candidates)
    except Exception as e:
        return f"Error: {e}"
