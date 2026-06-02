"""Map raw Hugging Face rows to canonical RestaurantRecord objects."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

import pandas as pd

from config.settings import settings
from domain.models import BudgetBucket, RestaurantRecord

logger = logging.getLogger(__name__)

# Source column names in ManikaSaini/zomato-restaurant-recommendation
COL_NAME = "name"
COL_ADDRESS = "address"
COL_AREA = "location"
COL_CUISINES = "cuisines"
COL_COST = "approx_cost(for two people)"
COL_RATE = "rate"
COL_REST_TYPE = "rest_type"
COL_ONLINE_ORDER = "online_order"
COL_BOOK_TABLE = "book_table"
COL_DISH_LIKED = "dish_liked"
COL_LISTED_IN_TYPE = "listed_in(type)"
COL_LISTED_IN_CITY = "listed_in(city)"

REQUIRED_SOURCE_COLUMNS = {
    COL_NAME,
    COL_ADDRESS,
    COL_CUISINES,
    COL_RATE,
}

LOCATION_ALIASES = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "banglore": "Bangalore",
    "bengalore": "Bangalore",
    "btm bangalore": "Bangalore",
}

INVALID_CITY_TAILS = frozenset(
    {
        "india",
        "karnataka",
        "delivery only",
        "1st stage",
        "2nd stage",
        "3rd stage",
        "4th stage",
        "5th stage",
    }
)

BANGALORE_TOKENS = ("bangalore", "bengaluru", "banglore", "bengalore")

CATEGORICAL_COST_MAP = {
    "low": BudgetBucket.LOW,
    "medium": BudgetBucket.MEDIUM,
    "high": BudgetBucket.HIGH,
    "cheap": BudgetBucket.LOW,
    "moderate": BudgetBucket.MEDIUM,
    "expensive": BudgetBucket.HIGH,
}


class SchemaValidationError(ValueError):
    """Raised when the dataset schema does not match expectations."""


def validate_source_schema(df: pd.DataFrame) -> None:
    """Fail fast if required source columns are missing."""
    missing = REQUIRED_SOURCE_COLUMNS - set(df.columns)
    if missing:
        raise SchemaValidationError(
            f"Dataset missing required columns: {sorted(missing)}. "
            f"Found: {list(df.columns)}"
        )


def _normalize_city(raw: Optional[str]) -> Optional[str]:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    text = str(raw).strip()
    if not text:
        return None
    key = text.lower()
    if key in LOCATION_ALIASES:
        return LOCATION_ALIASES[key]
    # Title-case multi-word cities; keep known aliases applied first
    if text.lower().endswith("bangalore") or "bangalore" in key:
        return "Bangalore"
    return text.title()


def extract_city_from_address(address: Any) -> Optional[str]:
    """
    Derive city from address.

    Prefer Bangalore when any segment mentions it; otherwise use the last
    valid comma-separated segment, skipping state/country-only tails.
    """
    if address is None or (isinstance(address, float) and pd.isna(address)):
        return None
    text = str(address).strip()
    if not text:
        return None
    lower = text.lower()
    if any(token in lower for token in BANGALORE_TOKENS):
        return "Bangalore"

    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        return None

    candidate = _normalize_city(parts[-1])
    if not candidate or candidate.lower() in INVALID_CITY_TAILS:
        return None
    return candidate


def parse_rating(raw: Any) -> Optional[float]:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    text = str(raw).strip()
    if text.upper() in ("NEW", "-", "", "NAN"):
        return None
    match = re.search(r"([\d.]+)", text)
    if not match:
        return None
    value = float(match.group(1))
    if value < 0 or value > 5:
        return None
    return round(value, 2)


def parse_cost(raw: Any) -> Optional[float]:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    text = str(raw).strip().lower()
    if not text or text in ("-", "nan"):
        return None
    if text in CATEGORICAL_COST_MAP:
        return None  # bucket assigned separately via categorical map
    cleaned = re.sub(r"[^\d.]", "", text)
    if not cleaned:
        return None
    value = float(cleaned)
    if value <= 0:
        return None
    return value


def parse_cuisines(raw: Any) -> list[str]:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return []
    parts = re.split(r"[,;]", str(raw))
    return [p.strip().lower() for p in parts if p.strip()]


def derive_cost_bucket(
    cost_for_two: Optional[float],
    raw_cost: Any,
    low_max: float,
    medium_max: float,
) -> Optional[BudgetBucket]:
    if cost_for_two is not None:
        if cost_for_two <= low_max:
            return BudgetBucket.LOW
        if cost_for_two <= medium_max:
            return BudgetBucket.MEDIUM
        return BudgetBucket.HIGH
    if raw_cost is not None and not (isinstance(raw_cost, float) and pd.isna(raw_cost)):
        key = str(raw_cost).strip().lower()
        if key in CATEGORICAL_COST_MAP:
            return CATEGORICAL_COST_MAP[key]
    return None


def _build_attributes(row: pd.Series) -> dict[str, Any]:
    attrs: dict[str, Any] = {}
    if COL_ADDRESS in row and pd.notna(row[COL_ADDRESS]):
        attrs["address"] = str(row[COL_ADDRESS]).strip()
    if COL_AREA in row and pd.notna(row[COL_AREA]):
        attrs["area"] = str(row[COL_AREA]).strip()
    if COL_REST_TYPE in row and pd.notna(row[COL_REST_TYPE]):
        attrs["rest_type"] = str(row[COL_REST_TYPE]).strip()
    if COL_ONLINE_ORDER in row and pd.notna(row[COL_ONLINE_ORDER]):
        attrs["online_order"] = str(row[COL_ONLINE_ORDER]).strip()
    if COL_BOOK_TABLE in row and pd.notna(row[COL_BOOK_TABLE]):
        attrs["book_table"] = str(row[COL_BOOK_TABLE]).strip()
    if COL_DISH_LIKED in row and pd.notna(row[COL_DISH_LIKED]):
        attrs["dish_liked"] = str(row[COL_DISH_LIKED]).strip()
    if COL_LISTED_IN_TYPE in row and pd.notna(row[COL_LISTED_IN_TYPE]):
        attrs["listed_in_type"] = str(row[COL_LISTED_IN_TYPE]).strip()
    if COL_LISTED_IN_CITY in row and pd.notna(row[COL_LISTED_IN_CITY]):
        attrs["listed_in_area"] = str(row[COL_LISTED_IN_CITY]).strip()
    return attrs


def normalize_row(
    row: pd.Series,
    row_index: int,
    *,
    low_max: float | None = None,
    medium_max: float | None = None,
) -> Optional[RestaurantRecord]:
    """Normalize a single dataset row; return None if row should be dropped."""
    low_max = low_max if low_max is not None else settings.budget_low_max
    medium_max = medium_max if medium_max is not None else settings.budget_medium_max

    name = row.get(COL_NAME)
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return None
    name = str(name).strip()
    if not name:
        return None

    rating = parse_rating(row.get(COL_RATE))
    if rating is None:
        return None

    raw_loc = row.get(COL_AREA)
    location = None
    if raw_loc is not None and not (isinstance(raw_loc, float) and pd.isna(raw_loc)):
        raw_loc_str = str(raw_loc).strip()
        if raw_loc_str:
            if raw_loc_str.lower() in BANGALORE_TOKENS:
                location = "Bangalore"
            else:
                location = raw_loc_str.title()

    if not location:
        location = extract_city_from_address(row.get(COL_ADDRESS))

    if not location:
        return None

    cuisines = parse_cuisines(row.get(COL_CUISINES))
    raw_cost = row.get(COL_COST) if COL_COST in row.index else None
    cost_for_two = parse_cost(raw_cost)
    cost_bucket = derive_cost_bucket(cost_for_two, raw_cost, low_max, medium_max)

    return RestaurantRecord(
        id=f"r{row_index}",
        name=name,
        location=location,
        cuisines=cuisines,
        rating=rating,
        cost_for_two=cost_for_two,
        cost_bucket=cost_bucket,
        attributes=_build_attributes(row),
    )


def normalize_dataframe(df: pd.DataFrame) -> list[RestaurantRecord]:
    """Validate schema and normalize all rows."""
    validate_source_schema(df)
    records: list[RestaurantRecord] = []
    dropped = 0

    for idx, row in df.iterrows():
        record = normalize_row(
            row,
            int(idx),
            low_max=settings.budget_low_max,
            medium_max=settings.budget_medium_max,
        )
        if record is None:
            dropped += 1
            continue
        records.append(record)

    logger.info(
        "Normalized %d records (%d rows dropped)",
        len(records),
        dropped,
    )
    if not records:
        raise SchemaValidationError("No valid restaurants after normalization")

    return records


def records_to_dataframe(records: list[RestaurantRecord]) -> pd.DataFrame:
    """Serialize records for parquet cache."""
    rows = []
    for r in records:
        rows.append(
            {
                "id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": ",".join(r.cuisines),
                "rating": r.rating,
                "cost_for_two": r.cost_for_two,
                "cost_bucket": r.cost_bucket.value if r.cost_bucket else None,
                "attributes_json": json.dumps(r.attributes),
            }
        )
    return pd.DataFrame(rows)


def dataframe_to_records(df: pd.DataFrame) -> list[RestaurantRecord]:
    """Deserialize records from parquet cache."""
    records: list[RestaurantRecord] = []
    for _, row in df.iterrows():
        cuisines = (
            [c.strip() for c in str(row["cuisines"]).split(",") if c.strip()]
            if pd.notna(row["cuisines"]) and str(row["cuisines"])
            else []
        )
        bucket = None
        if pd.notna(row.get("cost_bucket")) and str(row["cost_bucket"]):
            bucket = BudgetBucket(str(row["cost_bucket"]))
        cost = row.get("cost_for_two")
        attrs_raw = row.get("attributes_json", row.get("attributes", "{}"))
        if isinstance(attrs_raw, dict):
            attributes = attrs_raw
        else:
            attributes = json.loads(attrs_raw) if pd.notna(attrs_raw) else {}
        records.append(
            RestaurantRecord(
                id=str(row["id"]),
                name=str(row["name"]),
                location=str(row["location"]),
                cuisines=cuisines,
                rating=float(row["rating"]),
                cost_for_two=float(cost) if pd.notna(cost) else None,
                cost_bucket=bucket,
                attributes=attributes,
            )
        )
    return records
