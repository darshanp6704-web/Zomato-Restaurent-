"""Tests for UI input validation."""

from __future__ import annotations

from app.input_validation import parse_user_preferences
from domain.models import BudgetBucket


def test_parse_valid_preferences():
    prefs, err = parse_user_preferences(
        location="Bangalore",
        budget_raw="cheap",
        cuisine="Italian",
        min_rating=4.5,
        additional_notes=" family-friendly ",
    )
    assert err is None
    assert prefs is not None
    assert prefs.budget == BudgetBucket.LOW
    assert prefs.cuisine == "Italian"
    assert prefs.additional_notes == "family-friendly"


def test_empty_location_rejected():
    _, err = parse_user_preferences(
        location="  ",
        budget_raw="medium",
        cuisine="italian",
        min_rating=4.0,
    )
    assert err == "Location is required."


def test_invalid_budget_rejected():
    _, err = parse_user_preferences(
        location="Bangalore",
        budget_raw="luxury",
        cuisine="italian",
        min_rating=4.0,
    )
    assert "Invalid budget" in (err or "")


def test_rating_clamped():
    prefs, err = parse_user_preferences(
        location="Bangalore",
        budget_raw="medium",
        cuisine="italian",
        min_rating=99.0,
    )
    assert err is None
    assert prefs is not None
    assert prefs.min_rating == 5.0
