"""Input validation at the UI boundary."""

from __future__ import annotations

from typing import Optional

from config.settings import settings
from domain.models import BudgetBucket, UserPreferences


def clamp_rating(value: float) -> float:
    return max(0.0, min(5.0, value))


def sanitize_notes(notes: Optional[str]) -> Optional[str]:
    if notes is None:
        return None
    text = notes.strip()
    if not text:
        return None
    text = "".join(ch for ch in text if ch == "\n" or ch >= " ")
    max_len = settings.max_additional_notes_length
    if len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return text


def parse_user_preferences(
    *,
    location: str,
    budget_raw: str,
    cuisine: str,
    min_rating: float,
    additional_notes: Optional[str] = None,
) -> tuple[Optional[UserPreferences], Optional[str]]:
    """
    Validate raw UI input. Returns (preferences, error_message).
    """
    location = (location or "").strip()
    cuisine = (cuisine or "").strip()
    if not location:
        return None, "Location is required."
    if not cuisine:
        return None, "Cuisine is required."

    try:
        budget = UserPreferences.parse_budget(budget_raw)
    except ValueError as exc:
        return None, str(exc)

    try:
        prefs = UserPreferences(
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=clamp_rating(float(min_rating)),
            additional_notes=sanitize_notes(additional_notes),
        )
    except ValueError as exc:
        return None, f"Invalid input: {exc}"
    return prefs, None
