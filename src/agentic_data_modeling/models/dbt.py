"""dbt model domain objects."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DbtModelType(StrEnum):
    STAGING = "staging"
    INTERMEDIATE = "intermediate"
    MART = "mart"


class DbtMaterialization(StrEnum):
    VIEW = "view"
    TABLE = "table"
    INCREMENTAL = "incremental"
    EPHEMERAL = "ephemeral"


class DbtColumnDef(BaseModel):
    name: str
    description: str = ""
    data_type: str = ""
    tests: list[str] = Field(default_factory=list)


class DbtTest(BaseModel):
    name: str
    column: str | None = None
    config: dict[str, object] = Field(default_factory=dict)


class DbtModel(BaseModel):
    name: str
    model_type: DbtModelType
    materialization: DbtMaterialization = DbtMaterialization.VIEW
    description: str = ""
    sql: str = ""
    columns: list[DbtColumnDef] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class DbtSource(BaseModel):
    name: str
    description: str = ""
    tables: list[str] = Field(default_factory=list)
    database: str = ""
    schema_name: str = "main"


class DbtProject(BaseModel):
    name: str
    sources: list[DbtSource] = Field(default_factory=list)
    models: list[DbtModel] = Field(default_factory=list)
