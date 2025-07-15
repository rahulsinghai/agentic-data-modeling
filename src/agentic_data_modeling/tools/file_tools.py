"""File I/O tools for reading and writing artifacts."""

from __future__ import annotations

from pathlib import Path

from langchain_core.tools import tool


@tool
def read_file(file_path: str) -> str:
    """Read a file and return its contents.

    Args:
        file_path: Path to the file.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    try:
        return path.read_text()
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_artifact(file_path: str, content: str) -> str:
    """Write content to a file, creating directories as needed.

    Args:
        file_path: Destination path.
        content: File content to write.
    """
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Written: {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def list_directory(dir_path: str) -> str:
    """List files in a directory.

    Args:
        dir_path: Directory path.
    """
    path = Path(dir_path)
    if not path.is_dir():
        return f"Error: Not a directory: {dir_path}"
    entries = sorted(path.iterdir())
    if not entries:
        return f"Empty directory: {dir_path}"
    lines = []
    for e in entries:
        suffix = "/" if e.is_dir() else ""
        lines.append(f"  {e.name}{suffix}")
    return "\n".join(lines)
