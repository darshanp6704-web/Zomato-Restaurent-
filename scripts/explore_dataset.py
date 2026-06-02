#!/usr/bin/env python3
"""Profile the Hugging Face Zomato dataset (Phase 1 exploration)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from config.settings import settings
from data.loader import load_raw_dataset
from data.normalizer import (
    COL_COST,
    COL_RATE,
    extract_city_from_address,
    parse_cost,
    parse_rating,
)


def main() -> None:
    print(f"Dataset: {settings.dataset_id}")
    df = load_raw_dataset()
    print(f"\nRows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    print("\n--- Null rates ---")
    for col in df.columns:
        print(f"  {col}: {df[col].isnull().mean():.3f}")

    print("\n--- Cost percentiles ---")
    costs = df[COL_COST].apply(parse_cost).dropna()
    print(costs.describe(percentiles=[0.25, 0.5, 0.75]))

    print("\n--- Rating samples ---")
    parsed = df[COL_RATE].apply(parse_rating)
    print(f"  Parseable ratings: {parsed.notna().sum()} / {len(df)}")
    print(f"  Range: {parsed.min()} - {parsed.max()}")

    print("\n--- Cities (from address) ---")
    cities = df["address"].apply(extract_city_from_address)
    print(cities.value_counts().head(15))

    print("\n--- Configured budget thresholds ---")
    print(f"  BUDGET_LOW_MAX={settings.budget_low_max}")
    print(f"  BUDGET_MEDIUM_MAX={settings.budget_medium_max}")


if __name__ == "__main__":
    main()
