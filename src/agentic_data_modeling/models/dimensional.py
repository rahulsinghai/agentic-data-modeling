"""Dimensional modeling domain models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SCDType(StrEnum):
    TYPE_0 = "type_0"
    TYPE_1 = "type_1"
    TYPE_2 = "type_2"


class DimensionType(StrEnum):
    REGULAR = "regular"
    DEGENERATE = "degenerate"
    JUNK = "junk"
    ROLE_PLAYING = "role_playing"
    CONFORMED = "conformed"


class ColumnMapping(BaseModel):
    source_table: str
    source_column: str
    target_column: str
    transformation: str | None = None


class DimensionAttribute(BaseModel):
    name: str
    data_type: str = "VARCHAR"
    description: str = ""
    scd_type: SCDType = SCDType.TYPE_1
    source_mapping: ColumnMapping | None = None


class Dimension(BaseModel):
    name: str
    description: str = ""
    dimension_type: DimensionType = DimensionType.REGULAR
    primary_key: str = ""
    attributes: list[DimensionAttribute] = Field(default_factory=list)
    source_tables: list[str] = Field(default_factory=list)


class FactMeasure(BaseModel):
    name: str
    data_type: str = "DOUBLE"
    aggregation: str = "sum"
    description: str = ""
    source_mapping: ColumnMapping | None = None


class FactDimensionLink(BaseModel):
    dimension_name: str
    foreign_key: str
    relationship: str = "many_to_one"


class Fact(BaseModel):
    name: str
    description: str = ""
    grain: str = ""
    measures: list[FactMeasure] = Field(default_factory=list)
    dimension_links: list[FactDimensionLink] = Field(default_factory=list)
    degenerate_dimensions: list[str] = Field(default_factory=list)
    source_tables: list[str] = Field(default_factory=list)


class DimensionalModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = "dimensional_model"
    description: str = ""
    # Accept both "facts" and "fact_tables" (LLM sometimes uses the latter)
    facts: list[Fact] = Field(
        default_factory=list,
        validation_alias=AliasChoices("facts", "fact_tables"),
    )
    # Accept both "dimensions" and "dimension_tables"
    dimensions: list[Dimension] = Field(
        default_factory=list,
        validation_alias=AliasChoices("dimensions", "dimension_tables"),
    )
    business_requirements: str = ""
