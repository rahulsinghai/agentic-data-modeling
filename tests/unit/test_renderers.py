"""Unit tests for the Jinja2 renderer engine."""

from agentic_data_modeling.models.dbt import (
    DbtColumnDef,
    DbtModel,
    DbtModelType,
    DbtProject,
    DbtSource,
)
from agentic_data_modeling.models.quality import (
    QualityConfig,
    QualityRule,
    QualityRuleType,
)
from agentic_data_modeling.renderers.engine import render_template


class TestRenderers:
    def test_render_staging(self):
        model = DbtModel(
            name="stg_orders",
            model_type=DbtModelType.STAGING,
            columns=[
                DbtColumnDef(name="order_id"),
                DbtColumnDef(name="customer_id"),
                DbtColumnDef(name="amount"),
            ],
            depends_on=["raw"],
        )
        result = render_template("dbt_staging.sql.j2", model=model)
        assert "order_id" in result
        assert "source(" in result

    def test_render_schema(self):
        project = DbtProject(
            name="test",
            models=[
                DbtModel(
                    name="stg_orders",
                    model_type=DbtModelType.STAGING,
                    description="Staging orders",
                    columns=[
                        DbtColumnDef(
                            name="order_id", description="PK", tests=["not_null", "unique"]
                        ),
                    ],
                )
            ],
        )
        result = render_template("dbt_schema.yml.j2", project=project)
        assert "stg_orders" in result
        assert "not_null" in result

    def test_render_sources(self):
        source = DbtSource(name="raw", tables=["orders", "customers"], schema_name="main")
        result = render_template("dbt_sources.yml.j2", source=source)
        assert "raw" in result
        assert "orders" in result

    def test_render_quality_rules(self):
        config = QualityConfig(
            model_name="ecommerce",
            rules=[
                QualityRule(
                    name="pk_not_null",
                    rule_type=QualityRuleType.NOT_NULL,
                    table="dim_customer",
                    column="customer_key",
                )
            ],
        )
        result = render_template("quality_rules.yml.j2", config=config)
        assert "pk_not_null" in result
        assert "dim_customer" in result
