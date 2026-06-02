"""Unit tests for data normalization (Phase 1)."""

from __future__ import annotations

import pandas as pd
import pytest

from data.normalizer import (
    COL_ADDRESS,
    COL_COST,
    COL_CUISINES,
    COL_NAME,
    COL_RATE,
    SchemaValidationError,
    derive_cost_bucket,
    extract_city_from_address,
    normalize_dataframe,
    normalize_row,
    parse_cuisines,
    parse_rating,
    validate_source_schema,
)
from domain.models import BudgetBucket


def test_parse_rating_fraction():
    assert parse_rating("4.1/5") == 4.1


def test_parse_rating_invalid():
    assert parse_rating("NEW") is None
    assert parse_rating(None) is None


def test_parse_cuisines_split():
    assert parse_cuisines("North Indian, Chinese") == ["north indian", "chinese"]


def test_extract_city_bangalore_alias():
    assert extract_city_from_address("1st Main, Bengaluru") == "Bangalore"
    assert (
        extract_city_from_address(
            "942, 21st Main Road, 2nd Stage, Banashankari, Bangalore"
        )
        == "Bangalore"
    )


def test_extract_city_invalid_tail():
    assert extract_city_from_address("Some Street, Karnataka") is None


def test_derive_cost_buckets():
    assert derive_cost_bucket(300, None, 400, 550) == BudgetBucket.LOW
    assert derive_cost_bucket(400, None, 400, 550) == BudgetBucket.LOW
    assert derive_cost_bucket(450, None, 400, 550) == BudgetBucket.MEDIUM
    assert derive_cost_bucket(600, None, 400, 550) == BudgetBucket.HIGH


def test_normalize_row_valid():
    row = pd.Series(
        {
            COL_NAME: "Test Bistro",
            COL_ADDRESS: "123 Road, Koramangala, Bangalore",
            COL_CUISINES: "Italian, Pizza",
            COL_RATE: "4.2/5",
            COL_COST: "500",
            "location": "Koramangala",
        }
    )
    record = normalize_row(row, 0, low_max=400, medium_max=550)
    assert record is not None
    assert record.name == "Test Bistro"
    assert record.location == "Koramangala"
    assert record.rating == 4.2
    assert record.cost_for_two == 500.0
    assert record.cost_bucket == BudgetBucket.MEDIUM
    assert record.attributes["area"] == "Koramangala"


def test_normalize_row_drops_missing_rating():
    row = pd.Series(
        {
            COL_NAME: "No Rating Cafe",
            COL_ADDRESS: "123 Road, Bangalore",
            COL_CUISINES: "Cafe",
            COL_RATE: "NEW",
            COL_COST: "300",
        }
    )
    assert normalize_row(row, 1) is None


def test_validate_source_schema_missing_columns():
    with pytest.raises(SchemaValidationError):
        validate_source_schema(pd.DataFrame({"foo": [1]}))


def test_normalize_dataframe_minimal():
    df = pd.DataFrame(
        [
            {
                COL_NAME: "A",
                COL_ADDRESS: "X, Bangalore",
                COL_CUISINES: "Chinese",
                COL_RATE: "4.0/5",
                COL_COST: "300",
            },
            {
                COL_NAME: "B",
                COL_ADDRESS: "Y, Bangalore",
                COL_CUISINES: "Italian",
                COL_RATE: "3.5/5",
                COL_COST: "600",
            },
        ]
    )
    records = normalize_dataframe(df)
    assert len(records) == 2
    assert records[0].cost_bucket == BudgetBucket.LOW
    assert records[1].cost_bucket == BudgetBucket.HIGH
