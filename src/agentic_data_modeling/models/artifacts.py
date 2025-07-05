"""Output artifact models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ERDiagram(BaseModel):
    mermaid_code: str = ""
    title: str = ""
    description: str = ""


class DDLStatement(BaseModel):
    table_name: str
    ddl: str
    dialect: str = "duckdb"


class DDLBundle(BaseModel):
    statements: list[DDLStatement] = Field(default_factory=list)
    dialect: str = "duckdb"


class DocumentationPage(BaseModel):
    title: str
    content: str = ""
    section: str = "overview"
