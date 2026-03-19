"""Rich callback handler for real-time pipeline logging."""

from __future__ import annotations

import json
import time
from pathlib import Path

from langchain_core.callbacks.base import BaseCallbackHandler
from rich.console import Console

# Tool output prefixes that indicate a recoverable but logged error.
_ERROR_PREFIXES = (
    "Error:",
    "Invalid ",
    "SQL Error:",
    "Error profiling",
    "Error loading",
)

# After this many consecutive tool errors the pipeline aborts.
_MAX_CONSECUTIVE_ERRORS = 5


def _fmt_input(tool_name: str, input_str: str) -> str:
    """Return a concise human-readable summary of a tool's input arguments."""
    try:
        args: dict = json.loads(input_str)
    except Exception:
        return input_str[:80]

    match tool_name:
        case "list_directory":
            return Path(args.get("dir_path", "")).name or args.get("dir_path", "")
        case "load_csv" | "load_json" | "read_file":
            return Path(args.get("file_path", "")).name
        case "write_artifact":
            return Path(args.get("file_path", "")).name
        case "describe_table" | "detect_primary_keys":
            return args.get("table_name", "")
        case "profile_column":
            return f"{args.get('table_name')}.{args.get('column_name')}"
        case "detect_foreign_keys":
            return args.get("table_name", "")
        case "run_query":
            sql = args.get("sql", "").strip().replace("\n", " ")
            return sql[:70] + ("…" if len(sql) > 70 else "")
        case "check_grain":
            return args.get("fact_name", "")
        case "validate_star_schema":
            return "(dimensional model JSON)"
        case "render_dbt_model" | "render_dbt_schema" | "render_dbt_sources":
            return "(dbt spec JSON)"
        case "render_ddl" | "render_mermaid_erd":
            return "(model JSON)"
        case "render_quality_rules":
            return "(quality config JSON)"
        case _:
            parts = [f"{v}" for v in list(args.values())[:2]]
            return ", ".join(str(p)[:40] for p in parts)


def _fmt_output(tool_name: str, output: str) -> str:
    """Return a concise human-readable summary of a tool's output."""
    if any(output.startswith(p) for p in _ERROR_PREFIXES):
        return output.split("\n")[0][:120]

    match tool_name:
        case "list_directory":
            lines = [ln.strip() for ln in output.strip().splitlines() if ln.strip()]
            names = ", ".join(ln.lstrip("• ") for ln in lines[:5])
            suffix = f" (+{len(lines) - 5} more)" if len(lines) > 5 else ""
            return f"{len(lines)} files: {names}{suffix}"
        case "load_csv" | "load_json":
            # e.g. "Loaded 50 rows into table 'customers' from customers.csv"
            return output.strip()
        case "list_tables":
            tables = [ln.lstrip("- ").strip() for ln in output.splitlines() if ln.strip()]
            return f"{len(tables)} tables: {', '.join(tables)}"
        case "describe_table":
            lines = [ln for ln in output.splitlines() if ln and not ln.startswith("-")]
            cols = lines[1:]  # skip header
            names = ", ".join(c.split()[0] for c in cols[:6])
            suffix = f" (+{len(cols) - 6} more)" if len(cols) > 6 else ""
            return f"{len(cols)} columns: {names}{suffix}"
        case "profile_column":
            info: dict[str, str] = {}
            for line in output.splitlines():
                if ": " in line:
                    k, _, v = line.partition(": ")
                    info[k.strip()] = v.strip()
            return (
                f"type={info.get('Type', '?')}  "
                f"rows={info.get('Total rows', '?')}  "
                f"nulls={info.get('Null count', '?')}  "
                f"distinct={info.get('Distinct count', '?')}"
            )
        case "detect_primary_keys":
            return output.strip()
        case "detect_foreign_keys":
            lines = [ln for ln in output.splitlines() if "->" in ln]
            if not lines:
                return output.strip()
            return f"{len(lines)} FK candidate(s): " + "; ".join(ln.strip() for ln in lines[:3])
        case "run_query":
            lines = output.strip().splitlines()
            return f"{len(lines) - 2} row(s)" if len(lines) > 2 else output.strip()[:80]
        case "validate_star_schema":
            first = output.strip().splitlines()[0] if output.strip() else output
            return first
        case "check_grain":
            for line in output.splitlines():
                if "Status:" in line:
                    return line.replace("Status:", "").strip()
            return output.splitlines()[0][:80]
        case "render_dbt_model" | "render_dbt_schema" | "render_dbt_sources":
            lines = [ln for ln in output.splitlines() if ln.strip()]
            return f"{len(lines)} lines rendered"
        case "render_ddl":
            lines = [ln for ln in output.splitlines() if ln.strip()]
            return f"DDL: {len(lines)} lines"
        case "render_mermaid_erd":
            lines = [ln for ln in output.splitlines() if ln.strip()]
            return f"Mermaid ERD: {len(lines)} lines"
        case "render_quality_rules":
            lines = [ln for ln in output.splitlines() if ln.strip()]
            return f"Quality rules YAML: {len(lines)} lines"
        case "write_artifact":
            return output.strip()
        case _:
            return output.replace("\n", " ")[:100]


class PipelineCallbackHandler(BaseCallbackHandler):
    """Logs every LLM request/response and tool call to a Rich console."""

    # Tell LangChain to re-raise exceptions from this handler instead of swallowing them.
    raise_error: bool = True

    def __init__(self, console: Console) -> None:
        super().__init__()
        self.console = console
        self._llm_start: float | None = None
        self._consecutive_tool_errors = 0
        self._pending_tool: str = ""  # tool name buffered from on_tool_start

    # ── LLM events ────────────────────────────────────────────────────────────

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs: object) -> None:
        model = (
            serialized.get("kwargs", {}).get("model_name")
            or serialized.get("kwargs", {}).get("model")
            or serialized.get("name", "LLM")
        )
        self._llm_start = time.monotonic()
        self.console.print(f"  [cyan]🤖 Thinking[/cyan]  [dim]{model}[/dim]")

    def on_llm_end(self, response: object, **kwargs: object) -> None:
        elapsed = f"{time.monotonic() - self._llm_start:.1f}s" if self._llm_start else ""
        usage = ""
        try:
            token_usage = response.llm_output.get("token_usage", {})  # type: ignore[union-attr]
            total = token_usage.get("total_tokens", 0)
            if total:
                usage = f", {total:,} tokens"
        except Exception:
            pass
        self.console.print(f"  [cyan]✓ Done[/cyan]        [dim]{elapsed}{usage}[/dim]")

    def on_llm_error(self, error: Exception, **kwargs: object) -> None:
        self.console.print(f"  [red]✗ LLM error:[/red] {error}")
        raise RuntimeError(f"LLM error: {error}") from error

    # ── Tool events ───────────────────────────────────────────────────────────

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs: object) -> None:
        name = serialized.get("name", "tool")
        self._pending_tool = name
        arg_summary = _fmt_input(name, input_str)
        self.console.print(f"    [yellow]⚙[/yellow] [bold]{name}[/bold]  [dim]{arg_summary}[/dim]")

    def on_tool_end(self, output: str, **kwargs: object) -> None:
        output_str = str(output)
        summary = _fmt_output(self._pending_tool, output_str)
        is_error = any(output_str.startswith(p) for p in _ERROR_PREFIXES)

        if is_error:
            self._consecutive_tool_errors += 1
            self.console.print(f"      [red]✗[/red] {summary}")
            if self._consecutive_tool_errors >= _MAX_CONSECUTIVE_ERRORS:
                raise RuntimeError(
                    f"Pipeline aborted after {self._consecutive_tool_errors} consecutive "
                    f"tool errors. Last: {output_str[:300]}"
                )
        else:
            self._consecutive_tool_errors = 0
            self.console.print(f"      [dim]↳ {summary}[/dim]")

    def on_tool_error(self, error: Exception, **kwargs: object) -> None:
        self.console.print(f"    [red]✗ Tool exception:[/red] {error}")
        raise RuntimeError(f"Tool raised exception: {error}") from error
