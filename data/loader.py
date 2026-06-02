"""Load Zomato dataset from Hugging Face with local normalized cache."""

from __future__ import annotations

import logging
import time
from typing import Optional

import pandas as pd
from datasets import load_dataset

from config.settings import settings
from data.normalizer import (
    dataframe_to_records,
    normalize_dataframe,
    records_to_dataframe,
)
from domain.models import RestaurantRecord

logger = logging.getLogger(__name__)


class DatasetLoadError(RuntimeError):
    """Raised when the Hugging Face dataset cannot be loaded."""


def load_raw_dataset(
    *,
    refresh: bool = False,
    dataset_id: Optional[str] = None,
    split: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load the raw dataset from Hugging Face as a pandas DataFrame.

    Retries up to 3 times on transient network errors.
    """
    dataset_id = dataset_id or settings.dataset_id
    split = split or settings.dataset_split
    last_error: Optional[Exception] = None

    for attempt in range(3):
        try:
            logger.info("Loading dataset %s (split=%s)", dataset_id, split)
            ds = load_dataset(dataset_id, split=split)
            return ds.to_pandas()
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                wait = 2**attempt
                logger.warning(
                    "Dataset load failed (attempt %d/3): %s. Retrying in %ds...",
                    attempt + 1,
                    exc,
                    wait,
                )
                time.sleep(wait)

    raise DatasetLoadError(
        "Unable to load restaurant data. Check your connection and try again."
    ) from last_error


def _load_from_cache() -> Optional[list[RestaurantRecord]]:
    path = settings.normalized_cache_file
    if not path.exists():
        return None
    logger.info("Loading normalized restaurants from cache: %s", path)
    df = pd.read_parquet(path)
    return dataframe_to_records(df)


def _save_to_cache(records: list[RestaurantRecord]) -> None:
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    path = settings.normalized_cache_file
    df = records_to_dataframe(records)
    df.to_parquet(path, index=False)
    logger.info("Saved %d normalized records to %s", len(records), path)


def load_restaurants(*, refresh: Optional[bool] = None) -> list[RestaurantRecord]:
    """
    Load normalized restaurant records.

    Uses parquet cache under data/cache/ unless refresh=True.
    Set REFRESH_DATASET=true in environment or pass refresh=True to re-download.
    """
    if refresh is None:
        refresh = settings.refresh_dataset

    if not refresh:
        cached = _load_from_cache()
        if cached is not None:
            return cached

    raw_df = load_raw_dataset(refresh=refresh)
    
    # Check if we are running in a production or resource-constrained environment
    import os
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
    is_production = os.getenv("PRODUCTION", "false").lower() == "true"
    
    if (is_railway or is_production) and len(raw_df) > 15000:
        logger.info("Restricting dataset memory footprint by sampling 15,000 rows for resource safety.")
        raw_df = raw_df.sample(n=15000, random_state=42).reset_index(drop=True)

    records = normalize_dataframe(raw_df)
    _save_to_cache(records)
    return records
