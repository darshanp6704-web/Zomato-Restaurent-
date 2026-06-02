"""Prompt templates for Groq recommendations."""

from __future__ import annotations

import json
from typing import Any

from domain.models import RestaurantRecord, UserPreferences

SYSTEM_PROMPT = """You are a restaurant recommendation assistant for a Zomato-style dataset.
Use ONLY restaurants from the CANDIDATES list. Do not invent restaurants.
Rank by fit to user preferences (location, budget, cuisine, minimum rating, additional notes).
Output valid JSON only with no markdown fences or extra text."""


def _serialize_candidates(candidates: list[RestaurantRecord]) -> str:
    rows: list[dict[str, Any]] = []
    for r in candidates:
        rows.append(
            {
                "id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": r.cuisines,
                "rating": r.rating,
                "cost_for_two": r.cost_for_two,
                "cost_bucket": r.cost_bucket.value if r.cost_bucket else None,
                "area": r.attributes.get("area"),
            }
        )
    return json.dumps(rows, indent=2)


def build_messages(
    prefs: UserPreferences,
    candidates: list[RestaurantRecord],
    top_n: int,
) -> list[dict[str, str]]:
    notes = prefs.additional_notes or "None"
    user_content = f"""Preferences:
- Location: {prefs.location}
- Budget: {prefs.budget.value}
- Cuisine: {prefs.cuisine}
- Minimum rating: {prefs.min_rating}
- Additional notes: {notes}

Candidates:
{_serialize_candidates(candidates)}

Return JSON with keys:
- summary (optional string, one short paragraph)
- recommendations (array of exactly up to {top_n} items)

Each recommendation object must have rank (int), restaurant_id (string),
name (string), and explanation (string).
Do not include restaurants not in the candidates list."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def build_fix_json_messages(previous_response: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": "Return valid JSON only. No markdown."},
        {
            "role": "user",
            "content": f"Fix this to valid JSON only:\n{previous_response[:8000]}",
        },
    ]
