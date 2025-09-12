"""Unit tests for Pydantic domain models."""

from agentic_data_modeling.models.artifacts import DDLStatement, ERDiagram
from agentic_data_modeling.models.dbt import DbtModel, DbtModelType, DbtProject
from agentic_data_modeling.models.dimensional import (
    DimensionalModel,
    FactMeasure,
    SCDType,
)
from agentic_data_modeling.models.quality import QualityConfig, QualityRule, QualityRuleType
from agentic_data_modeling.models.source import ColumnProfile, DataType, SourceTableProfile


class TestSourceModels:
    def test_column_profile_null_pct(self):
        col = ColumnProfile(
            name="test", data_type=DataType.STRING, null_count=10, total_count=100
        )
        assert col.null_pct == 10.0

    def test_column_profile_uniqueness(self):
        col = ColumnProfile(
            name="id", data_type=DataType.INTEGER, distinct_count=100, total_count=100
        )
        assert col.uniqueness_pct == 100.0

    def test_source_table_profile(self):
        profile = SourceTableProfile(table_name="orders", row_count=1000, column_count=5)
        assert profile.table_name == "orders"
        assert profile.row_count == 1000


class TestDimensionalModels:
    def test_dimensional_model_roundtrip(self, sample_dimensional_model):
        json_str = sample_dimensional_model.model_dump_json()
        restored = DimensionalModel.model_validate_json(json_str)
        assert restored.name == "test_ecommerce"
        assert len(restored.facts) == 1
        assert len(restored.dimensions) == 2

    def test_scd_types(self):
        assert SCDType.TYPE_2 == "type_2"

    def test_fact_measures(self):
        m = FactMeasure(name="revenue", data_type="DECIMAL", aggregation="sum")
        assert m.aggregation == "sum"


class TestDbtModels:
    def test_dbt_model(self):
        model = DbtModel(
            name="stg_orders",
            model_type=DbtModelType.STAGING,
            description="Staging orders",
        )
        assert model.model_type == DbtModelType.STAGING

    def test_dbt_project(self):
        project = DbtProject(name="ecommerce")
        assert project.name == "ecommerce"
        assert project.models == []


class TestQualityModels:
    def test_quality_rule(self):
        rule = QualityRule(
            name="pk_not_null",
            rule_type=QualityRuleType.NOT_NULL,
            table="dim_customer",
            column="customer_key",
        )
        assert rule.severity.value == "error"

    def test_quality_config(self):
        config = QualityConfig(model_name="ecommerce", rules=[])
        assert config.model_name == "ecommerce"


class TestArtifactModels:
    def test_erd(self):
        erd = ERDiagram(title="test", mermaid_code="erDiagram")
        assert erd.title == "test"

    def test_ddl(self):
        ddl = DDLStatement(table_name="orders", ddl="CREATE TABLE orders (id INT);")
        assert ddl.dialect == "duckdb"
