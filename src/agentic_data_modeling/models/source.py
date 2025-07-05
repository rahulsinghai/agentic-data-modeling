"""Source data profiling models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DataType(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    JSON = "json"
    UNKNOWN = "unknown"


class ColumnProfile(BaseModel):
    name: str
    data_type: DataType
    nullable: bool = True
    distinct_count: int = 0
    null_count: int = 0
    total_count: int = 0
    min_value: str | None = None
    max_value: str | None = None
    mean_value: float | None = None
    sample_values: list[str] = Field(default_factory=list)
    is_potential_pk: bool = False
    is_potential_fk: bool = False
    fk_references: str | None = None

    @property
    def null_pct(self) -> float:
        return (self.null_count / self.total_count * 100) if self.total_count else 0.0

    @property
    def uniqueness_pct(self) -> float:
        return (self.distinct_count / self.total_count * 100) if self.total_count else 0.0


class SourceTableProfile(BaseModel):
    table_name: str
    row_count: int = 0
    column_count: int = 0
    columns: list[ColumnProfile] = Field(default_factory=list)
    primary_key_candidates: list[str] = Field(default_factory=list)
    foreign_key_candidates: list[dict[str, str]] = Field(default_factory=list)
    grain_description: str | None = None
