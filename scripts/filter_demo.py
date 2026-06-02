#!/usr/bin/env python3
"""Filter-only demo: structured search without LLM (Phase 2 milestone)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_restaurants
from domain.filters import filter_restaurants
from domain.models import BudgetBucket, UserPreferences


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter restaurants (no LLM)")
    parser.add_argument("--location", default="Bangalore")
    parser.add_argument("--budget", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--cuisine", default="italian")
    parser.add_argument("--min-rating", type=float, default=4.0)
    parser.add_argument("--limit", type=int, default=10, help="Rows to print")
    args = parser.parse_args()

    records = load_restaurants()
    prefs = UserPreferences(
        location=args.location,
        budget=BudgetBucket(args.budget),
        cuisine=args.cuisine,
        min_rating=args.min_rating,
    )

    result = filter_restaurants(prefs, records)

    if result.is_empty:
        print(result.message)
        return

    print(
        f"Matched {result.total_matched} restaurants"
        + (" (capped for LLM)" if result.capped else "")
    )
    print(f"Showing top {min(args.limit, len(result.candidates))} by rating:\n")

    for i, r in enumerate(result.candidates[: args.limit], 1):
        cuisines = ", ".join(r.cuisines)
        cost = f"₹{r.cost_for_two:.0f}" if r.cost_for_two else "N/A"
        bucket = r.cost_bucket.value if r.cost_bucket else "N/A"
        area = r.attributes.get("area", "")
        area_str = f" ({area})" if area else ""
        print(f"{i}. {r.name}{area_str}")
        print(f"   {cuisines} | ★ {r.rating} | {cost} | budget: {bucket}")
        print()


if __name__ == "__main__":
    main()
