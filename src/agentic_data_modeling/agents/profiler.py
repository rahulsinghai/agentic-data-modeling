"""Profiler sub-agent.

Pre-loads source files into DuckDB, runs all profiling queries in Python,
then asks the LLM only to synthesize results into structured JSON.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from agentic_data_modeling.agents.state import AgentState
from agentic_data_modeling.llm import get_llm
from agentic_data_modeling.tools.duckdb_tools import locked_connection

logger = logging.getLogger(__name__)


def _preload_source_files(source_dir: str) -> list[str]:
    """Load all data files from source_dir into DuckDB. Returns table names."""
    src_path = Path(source_dir)
    if not src_path.is_dir():
        return []

    loaders = {
        ".csv": "read_csv_auto",
        ".json": "read_json_auto",
        ".parquet": "read_parquet",
    }
    table_names = []
    for f in sorted(src_path.iterdir()):
        if not f.is_file() or f.suffix.lower() not in loaders:
            continue
        table_name = f.stem
        reader = loaders[f.suffix.lower()]
        try:
            with locked_connection() as conn:
                conn.execute(
                    f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {reader}('{f}')"
                )
                count = conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]
            logger.info("Loaded %d rows into '%s' from %s", count, table_name, f.name)
            table_names.append(table_name)
        except Exception as e:
            logger.warning("Failed to load %s: %s", f.name, e)
    return table_names


def _describe_table(conn, table_name: str) -> list[dict]:
    """Return column info for a table."""
    cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
    return [{"name": c[0], "type": c[1], "nullable": c[2]} for c in cols]


def _profile_column(conn, table_name: str, column_name: str) -> dict:
    """Profile a single column and return stats as a dict."""
    try:
        type_row = conn.execute(
            f'SELECT typeof("{column_name}") FROM {table_name} LIMIT 1'
        ).fetchone()
        data_type = type_row[0] if type_row else "UNKNOWN"

        row = conn.execute(f"""
            SELECT
                count(*) as total,
                count("{column_name}") as non_null,
                count(*) - count("{column_name}") as null_count,
                count(DISTINCT "{column_name}") as distinct_count,
                min("{column_name}")::varchar as min_val,
                max("{column_name}")::varchar as max_val
            FROM {table_name}
        """).fetchone()

        samples = [
            r[0]
            for r in conn.execute(f"""
                SELECT DISTINCT "{column_name}"::varchar as val
                FROM {table_name}
                WHERE "{column_name}" IS NOT NULL
                LIMIT 5
            """).fetchall()
        ]

        mean_val = None
        try:
            mean_row = conn.execute(
                f'SELECT avg("{column_name}")::float FROM {table_name}'
            ).fetchone()
            if mean_row and mean_row[0] is not None:
                mean_val = round(mean_row[0], 4)
        except Exception:
            pass

        return {
            "column": column_name,
            "type": data_type,
            "total_rows": row[0],
            "non_null": row[1],
            "null_count": row[2],
            "distinct_count": row[3],
            "min": row[4],
            "max": row[5],
            "mean": mean_val,
            "samples": samples,
        }
    except Exception as e:
        return {"column": column_name, "error": str(e)}


def _detect_primary_keys(conn, table_name: str) -> list[str]:
    """Detect candidate primary keys by checking uniqueness and non-null."""
    cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
    total = conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]
    candidates = []
    for col in cols:
        col_name = col[0]
        row = conn.execute(f"""
            SELECT
                count(DISTINCT "{col_name}") as dist,
                count(*) - count("{col_name}") as nulls
            FROM {table_name}
        """).fetchone()
        if row[0] == total and row[1] == 0:
            candidates.append(col_name)
    return candidates


def _detect_foreign_keys(conn, table_name: str, all_tables: list[str]) -> list[str]:
    """Detect potential FK relationships by matching column values."""
    source_cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
    source_types = {r[0]: r[1] for r in source_cols}
    fk_candidates = []

    for col_name, col_type in source_types.items():
        if not (col_name.endswith("_id") or col_name.endswith("_key")):
            continue
        for ref_table in all_tables:
            if ref_table == table_name:
                continue
            ref_cols = conn.execute(f"DESCRIBE {ref_table}").fetchall()
            ref_total = conn.execute(f"SELECT count(*) FROM {ref_table}").fetchone()[0]
            for ref_col in ref_cols:
                ref_col_name, ref_col_type = ref_col[0], ref_col[1]
                if ref_col_type != col_type:
                    continue
                ref_dist = conn.execute(
                    f'SELECT count(DISTINCT "{ref_col_name}") FROM {ref_table}'
                ).fetchone()[0]
                if ref_dist != ref_total:
                    continue
                orphans = conn.execute(f"""
                    SELECT count(*) FROM (
                        SELECT DISTINCT "{col_name}" FROM {table_name}
                        WHERE "{col_name}" IS NOT NULL
                        EXCEPT
                        SELECT DISTINCT "{ref_col_name}" FROM {ref_table}
                    )
                """).fetchone()[0]
                if orphans == 0:
                    fk_candidates.append(f"{table_name}.{col_name} -> {ref_table}.{ref_col_name}")
    return fk_candidates


def _run_all_profiling(table_names: list[str]) -> list[dict]:
    """Run all profiling queries in Python and return structured results."""
    results = []
    with locked_connection() as conn:
        for table_name in table_names:
            table_info: dict = {"table_name": table_name}

            # Describe columns
            columns = _describe_table(conn, table_name)
            table_info["columns"] = columns

            # Profile each column
            col_profiles = []
            for col in columns:
                profile = _profile_column(conn, table_name, col["name"])
                col_profiles.append(profile)
            table_info["column_profiles"] = col_profiles

            # Detect PKs
            table_info["primary_key_candidates"] = _detect_primary_keys(conn, table_name)

            # Detect FKs
            table_info["foreign_key_candidates"] = _detect_foreign_keys(
                conn, table_name, table_names
            )

            results.append(table_info)
    return results


SYNTHESIZE_PROMPT = """\
You are a Data Profiling Agent. You have been given pre-computed profiling results \
for all source tables. Your job is to analyze these results and produce a final \
structured JSON array of SourceTableProfile objects.

For each table, include:
- table_name
- grain (what one row represents)
- row_count
- columns (list with name, type, nullable, distinct_count, null_count, min, max, mean, samples)
- primary_key_candidates
- foreign_key_candidates
- data_quality_notes (any issues like high nulls, low cardinality, suspicious patterns)

Output ONLY valid JSON — no markdown fences, no explanation before or after.
"""


def profiler_node(state: AgentState) -> dict:
    source_dir = state.get("source_dir", "")

    # Pre-load all source files into DuckDB
    table_names = _preload_source_files(source_dir)

    # Run all profiling in Python (no LLM tool-calling needed)
    profiling_results = _run_all_profiling(table_names)

    # Ask LLM only to synthesize into structured JSON
    llm = get_llm()
    result = llm.invoke(
        [
            SystemMessage(content=SYNTHESIZE_PROMPT),
            HumanMessage(
                content=(
                    f"Here are the profiling results:\n\n"
                    f"{json.dumps(profiling_results, indent=2, default=str)}\n\n"
                    f"Requirements context: {state.get('requirements', 'N/A')}\n\n"
                    f"Produce the final SourceTableProfile JSON array."
                )
            ),
        ]
    )

    return {
        "messages": [result],
        "profiles_json": result.content,
        "completed_agents": ["profiler"],
    }
