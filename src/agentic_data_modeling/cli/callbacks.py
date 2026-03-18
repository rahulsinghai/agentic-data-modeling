"""Rich callback handler for real-time pipeline logging."""

from __future__ import annotations

import time

from langchain_core.callbacks.base import BaseCallbackHandler
from rich.console import Console


class PipelineCallbackHandler(BaseCallbackHandler):
    """Logs every LLM request/response and tool call to a Rich console."""

    def __init__(self, console: Console) -> None:
        super().__init__()
        self.console = console
        self._llm_start: float | None = None

    # ── LLM events ────────────────────────────────────────────────────────────

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs: object) -> None:
        model = (
            serialized.get("kwargs", {}).get("model_name")
            or serialized.get("kwargs", {}).get("model")
            or serialized.get("name", "LLM")
        )
        self._llm_start = time.monotonic()
        self.console.print(f"    [cyan]→[/cyan] Sending request  [dim]{model}[/dim]")

    def on_llm_end(self, response: object, **kwargs: object) -> None:
        elapsed = (
            f"{time.monotonic() - self._llm_start:.1f}s" if self._llm_start else ""
        )
        usage = ""
        try:
            token_usage = response.llm_output.get("token_usage", {})  # type: ignore[union-attr]
            total = token_usage.get("total_tokens", 0)
            if total:
                usage = f", {total} tokens"
        except Exception:
            pass
        self.console.print(
            f"    [cyan]←[/cyan] Reply received   [dim]{elapsed}{usage}[/dim]"
        )

    def on_llm_error(self, error: Exception, **kwargs: object) -> None:
        self.console.print(f"    [red]✗[/red] LLM error: {error}")

    # ── Tool events ───────────────────────────────────────────────────────────

    def on_tool_start(
        self, serialized: dict, input_str: str, **kwargs: object
    ) -> None:
        name = serialized.get("name", "tool")
        snippet = str(input_str)[:100].replace("\n", " ")
        self.console.print(
            f"    [yellow]⚙[/yellow]  Tool [bold]{name}[/bold]  [dim]{snippet}[/dim]"
        )

    def on_tool_end(self, output: str, **kwargs: object) -> None:
        snippet = str(output)[:120].replace("\n", " ")
        self.console.print(f"    [dim]   ↳ {snippet}[/dim]")

    def on_tool_error(self, error: Exception, **kwargs: object) -> None:
        self.console.print(f"    [red]✗[/red] Tool error: {error}")
