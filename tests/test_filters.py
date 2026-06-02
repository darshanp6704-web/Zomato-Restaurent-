"""Unit tests for structured filtering (Phase 2)."""

from __future__ import annotations

import time

import pytest

from config.settings import settings
from data.loader import load_restaurants
from domain.errors import FilterReasonCode
from domain.filters import (
    budget_matches,
    cuisine_matches,
    filter_restaurants,
    get_empty_filter_message,
    location_matches,
)
from domain.models import BudgetBucket, UserPreferences
from tests.fixtures.restaurants import FIXTURE_RESTAURANTS


def _prefs(**kwargs) -> UserPreferences:
    defaults = {
        "location": "Bangalore",
        "budget": BudgetBucket.MEDIUM,
        "cuisine": "italian",
        "min_rating": 3.5,
    }
    defaults.update(kwargs)
    return UserPreferences(**defaults)


def test_location_case_insensitive():
    assert location_matches("bangalore", "Bangalore")
    assert location_matches("BANGALORE", "Bangalore")


def test_location_exact_mode():
    assert location_matches("bangalore", "Bangalore", mode="exact")
    assert not location_matches("ban", "Bangalore", mode="exact")


def test_cuisine_exact_token_match():
    assert cuisine_matches("Italian", ["italian", "pizza"])
    assert cuisine_matches("north indian", ["north indian", "mughlai"])
    assert not cuisine_matches("Ital", ["italian"])  # EC-F-07 no partial


def test_cuisine_empty_list_no_match():
    record = FIXTURE_RESTAURANTS[0].model_copy(update={"cuisines": []})
    assert not cuisine_matches("italian", record.cuisines)


def test_budget_unknown_cost_excluded_by_default():
    record = FIXTURE_RESTAURANTS[4]  # cost_bucket None
    assert not budget_matches(BudgetBucket.MEDIUM, record)


def test_budget_unknown_cost_included_when_configured():
    record = FIXTURE_RESTAURANTS[4]
    assert budget_matches(BudgetBucket.MEDIUM, record, include_unknown_cost=True)


def test_filter_happy_path():
    result = filter_restaurants(_prefs(budget=BudgetBucket.MEDIUM), FIXTURE_RESTAURANTS)
    assert not result.is_empty
    assert result.reason_code is None
    ids = {r.id for r in result.candidates}
    assert "r1" in ids
    assert "r3" not in ids  # high budget
    assert "r4" not in ids  # Delhi
    assert "r5" not in ids  # unknown bucket
    assert "r6" not in ids  # rating 3.0 < 3.5


def test_filter_zero_results():
    result = filter_restaurants(
        _prefs(location="Mumbai", cuisine="italian"),
        FIXTURE_RESTAURANTS,
    )
    assert result.is_empty
    assert result.total_matched == 0
    assert result.reason_code == FilterReasonCode.NO_MATCHES.value
    assert result.message == get_empty_filter_message()


def test_filter_min_rating_boundary():
    result = filter_restaurants(
        _prefs(min_rating=4.5),
        FIXTURE_RESTAURANTS,
    )
    ids = {r.id for r in result.candidates}
    assert ids == {"r1"}  # only medium italian 4.5; r3 is high budget


def test_filter_budget_tier_high():
    result = filter_restaurants(
        _prefs(budget=BudgetBucket.HIGH, min_rating=4.0),
        FIXTURE_RESTAURANTS,
    )
    assert [r.id for r in result.candidates] == ["r3"]


def test_filter_candidate_cap():
    many = [
        FIXTURE_RESTAURANTS[0].model_copy(
            update={"id": f"cap{i}", "rating": 4.0 + i * 0.01}
        )
        for i in range(50)
    ]
    result = filter_restaurants(_prefs(), many, max_candidates=10)
    assert len(result.candidates) == 10
    assert result.total_matched == 50
    assert result.capped is True
    ratings = [r.rating for r in result.candidates]
    assert ratings == sorted(ratings, reverse=True)


def test_filter_stable_sort_on_rating_tie():
    tied = [
        FIXTURE_RESTAURANTS[0].model_copy(update={"id": "z", "rating": 4.5}),
        FIXTURE_RESTAURANTS[0].model_copy(update={"id": "a", "rating": 4.5}),
    ]
    result = filter_restaurants(_prefs(), tied)
    assert [r.id for r in result.candidates] == ["a", "z"]


def test_filter_deterministic_reproducible():
    prefs = _prefs()
    r1 = filter_restaurants(prefs, FIXTURE_RESTAURANTS)
    r2 = filter_restaurants(prefs, FIXTURE_RESTAURANTS)
    assert [c.id for c in r1.candidates] == [c.id for c in r2.candidates]


def test_user_preferences_validation():
    with pytest.raises(ValueError):
        UserPreferences(
            location="  ",
            budget=BudgetBucket.LOW,
            cuisine="italian",
            min_rating=4.0,
        )
    assert UserPreferences.parse_budget("cheap") == BudgetBucket.LOW


@pytest.mark.slow
def test_filter_performance_on_full_dataset():
    """Architecture target: filter < 1s on cached data."""
    records = load_restaurants()
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBucket.MEDIUM,
        cuisine="north indian",
        min_rating=4.0,
    )
    start = time.perf_counter()
    result = filter_restaurants(prefs, records)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, f"Filter took {elapsed:.2f}s"
    assert result.total_matched >= 0
