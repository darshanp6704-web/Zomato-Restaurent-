#!/usr/bin/env python3
"""Demo: load normalized restaurants and print sample rows."""

from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_restaurants


def main() -> None:
    start = time.perf_counter()
    records = load_restaurants()
    elapsed = time.perf_counter() - start
    print(f"Loaded {len(records)} restaurants in {elapsed:.2f}s\n")

    for record in records[:5]:
        print(f"  {record.id}: {record.name}")
        print(f"    location={record.location}, area={record.attributes.get('area')}")
        print(f"    cuisines={record.cuisines}")
        print(f"    rating={record.rating}, cost={record.cost_for_two}, bucket={record.cost_bucket}")
        print()


if __name__ == "__main__":
    main()
