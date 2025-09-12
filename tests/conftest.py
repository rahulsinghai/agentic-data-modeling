"""Shared test fixtures."""

from __future__ import annotations

import csv
from pathlib import Path

import duckdb
import pytest

from agentic_data_modeling.models.dimensional import (
    Dimension,
    DimensionalModel,
    DimensionAttribute,
    Fact,
    FactDimensionLink,
    FactMeasure,
)
from agentic_data_modeling.tools.duckdb_tools import set_connection


@pytest.fixture
def duckdb_conn():
    conn = duckdb.connect(":memory:")
    set_connection(conn)
    yield conn
    conn.close()
    set_connection(None)


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "orders.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "customer_id", "amount", "status", "order_date"])
        for i in range(1, 51):
            writer.writerow([i, (i % 10) + 1, round(10.0 + i * 2.5, 2), "completed", "2024-01-15"])
    return csv_path


@pytest.fixture
def sample_customers_csv(tmp_path: Path) -> Path:
    csv_path = tmp_path / "customers.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "name", "email"])
        for i in range(1, 11):
            writer.writerow([i, f"Customer {i}", f"c{i}@example.com"])
    return csv_path


@pytest.fixture
def sample_dimensional_model() -> DimensionalModel:
    return DimensionalModel(
        name="test_ecommerce",
        description="Test e-commerce model",
        facts=[
            Fact(
                name="fct_order_items",
                description="Order line items",
                grain="One row per order line item",
                measures=[
                    FactMeasure(name="quantity", data_type="INTEGER", aggregation="sum"),
                    FactMeasure(name="revenue", data_type="DECIMAL(10,2)", aggregation="sum"),
                ],
                dimension_links=[
                    FactDimensionLink(dimension_name="dim_customer", foreign_key="customer_key"),
                    FactDimensionLink(dimension_name="dim_product", foreign_key="product_key"),
                ],
                source_tables=["orders", "order_items"],
            )
        ],
        dimensions=[
            Dimension(
                name="dim_customer",
                description="Customer dimension",
                primary_key="customer_key",
                attributes=[
                    DimensionAttribute(name="customer_name", data_type="VARCHAR"),
                    DimensionAttribute(name="email", data_type="VARCHAR"),
                    DimensionAttribute(name="city", data_type="VARCHAR"),
                ],
                source_tables=["customers"],
            ),
            Dimension(
                name="dim_product",
                description="Product dimension",
                primary_key="product_key",
                attributes=[
                    DimensionAttribute(name="product_name", data_type="VARCHAR"),
                    DimensionAttribute(name="category", data_type="VARCHAR"),
                    DimensionAttribute(name="price", data_type="DECIMAL(10,2)"),
                ],
                source_tables=["products"],
            ),
        ],
    )
