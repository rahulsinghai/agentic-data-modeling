"""Data quality rule models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class QualityRuleType(StrEnum):
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    ACCEPTED_VALUES = "accepted_values"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    FRESHNESS = "freshness"
    ROW_COUNT = "row_count"
    CUSTOM_SQL = "custom_sql"


class QualitySeverity(StrEnum):
    WARN = "warn"
    ERROR = "error"


class QualityRule(BaseModel):
    name: str
    rule_type: QualityRuleType
    table: str
    column: str | None = None
    severity: QualitySeverity = QualitySeverity.ERROR
    description: str = ""
    config: dict[str, object] = Field(default_factory=dict)


class QualityConfig(BaseModel):
    rules: list[QualityRule] = Field(default_factory=list)
    model_name: str = ""
