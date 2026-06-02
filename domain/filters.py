"""Deterministic restaurant filtering (Phase 2)."""

from __future__ import annotations

import logging
from typing import Iterable, Literal

from config.settings import settings
from domain.errors import EMPTY_FILTER_MESSAGE, FilterReasonCode
from domain.models import BudgetBucket, FilterResult, RestaurantRecord, UserPreferences

logger = logging.getLogger(__name__)

LocationMatchMode = Literal["exact", "contains"]


def get_empty_filter_message() -> str:
    """User-facing message when no restaurants match (EC-F-01)."""
    return EMPTY_FILTER_MESSAGE


def _normalize_text(value: str) -> str:
    return value.strip().lower()


def location_matches(
    user_location: str,
    restaurant_location: str,
    *,
    mode: LocationMatchMode | None = None,
) -> bool:
    """Case-insensitive location match (EC-F-13)."""
    mode = mode or settings.location_match_mode  # type: ignore[assignment]
    user = _normalize_text(user_location)
    restaurant = _normalize_text(restaurant_location)
    if not user or not restaurant:
        return False
    if mode == "exact":
        return user == restaurant
    return user in restaurant or restaurant in user


def cuisine_matches(user_cuisine: str, restaurant_cuisines: list[str]) -> bool:
    """
    Case-insensitive cuisine match (EC-F-08).

    v1: exact token match after lowercasing; no partial/fuzzy match (EC-F-07).
    """
    if not restaurant_cuisines:
        return False
    needle = _normalize_text(user_cuisine)
    return any(_normalize_text(c) == needle for c in restaurant_cuisines)


def rating_matches(min_rating: float, restaurant_rating: float) -> bool:
    return restaurant_rating >= min_rating


def budget_matches(
    user_budget: BudgetBucket,
    restaurant: RestaurantRecord,
    *,
    include_unknown_cost: bool | None = None,
) -> bool:
    """
    Match user budget tier to restaurant cost_bucket (EC-F-09, EC-F-10).

    Unknown cost_bucket rows are excluded unless include_unknown_cost is True.
    """
    if include_unknown_cost is None:
        include_unknown_cost = settings.include_unknown_cost_in_budget
    if restaurant.cost_bucket is None:
        return include_unknown_cost
    return restaurant.cost_bucket == user_budget


def _apply_location_filter(
    records: Iterable[RestaurantRecord], prefs: UserPreferences
) -> list[RestaurantRecord]:
    return [r for r in records if location_matches(prefs.location, r.location)]


def _apply_cuisine_filter(
    records: Iterable[RestaurantRecord], prefs: UserPreferences
) -> list[RestaurantRecord]:
    return [r for r in records if cuisine_matches(prefs.cuisine, r.cuisines)]


def _apply_rating_filter(
    records: Iterable[RestaurantRecord], prefs: UserPreferences
) -> list[RestaurantRecord]:
    return [r for r in records if rating_matches(prefs.min_rating, r.rating)]


def _apply_budget_filter(
    records: Iterable[RestaurantRecord], prefs: UserPreferences
) -> list[RestaurantRecord]:
    return [r for r in records if budget_matches(prefs.budget, r)]


def _sort_and_cap(
    records: list[RestaurantRecord], max_candidates: int
) -> tuple[list[RestaurantRecord], bool]:
    """Pre-rank by rating desc; stable tie-break on id (EC-F-04)."""
    sorted_records = sorted(
        records,
        key=lambda r: (-r.rating, r.id),
    )
    if len(sorted_records) <= max_candidates:
        return sorted_records, False
    return sorted_records[:max_candidates], True


def filter_restaurants(
    prefs: UserPreferences,
    records: list[RestaurantRecord],
    *,
    max_candidates: int | None = None,
) -> FilterResult:
    """
    Apply filter chain: location → cuisine → min_rating → budget.

    Returns candidates (capped) and metadata for empty states.
    Does not call the LLM.
    """
    max_candidates = (
        max_candidates if max_candidates is not None else settings.max_candidates
    )

    matched = list(records)
    matched = _apply_location_filter(matched, prefs)
    matched = _apply_cuisine_filter(matched, prefs)
    matched = _apply_rating_filter(matched, prefs)
    matched = _apply_budget_filter(matched, prefs)

    total_matched = len(matched)

    if total_matched == 0:
        logger.info(
            "No matches for location=%s cuisine=%s budget=%s min_rating=%s",
            prefs.location,
            prefs.cuisine,
            prefs.budget.value,
            prefs.min_rating,
        )
        return FilterResult(
            candidates=[],
            total_matched=0,
            capped=False,
            message=get_empty_filter_message(),
            reason_code=FilterReasonCode.NO_MATCHES.value,
        )

    candidates, capped = _sort_and_cap(matched, max_candidates)
    logger.debug(
        "Filter matched %d (returning %d, capped=%s)",
        total_matched,
        len(candidates),
        capped,
    )
    return FilterResult(
        candidates=candidates,
        total_matched=total_matched,
        capped=capped,
        message=None,
        reason_code=None,
    )
