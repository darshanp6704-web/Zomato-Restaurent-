"""Data ingestion: load and normalize the Zomato dataset."""

from data.loader import load_raw_dataset, load_restaurants

__all__ = ["load_raw_dataset", "load_restaurants"]
