"""Parse and validate Groq JSON responses."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from config.settings import settings
from domain.models import RestaurantRecord, UserPreferences
from llm.models import LLMRecommendationItem, ParsedRecommendationResult

logger = logging.getLogger(__name__)


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
    return json.loads(cleaned[start : end + 1])


def _index_candidates(
    candidates: list[RestaurantRecord],
) -> dict[str, RestaurantRecord]:
    return {r.id: r for r in candidates}


def _match_by_name(
    name: str, candidates: list[RestaurantRecord]
) -> Optional[RestaurantRecord]:
    matches = [c for c in candidates if c.name.lower() == name.lower()]
    if len(matches) == 1:
        return matches[0]
    return None


def _template_explanation(prefs: UserPreferences) -> str:
    return (
        f"Highly rated match for your {prefs.cuisine} preference in "
        f"{prefs.location} within your {prefs.budget.value} budget."
    )


def build_fallback_result(
    prefs: UserPreferences,
    candidates: list[RestaurantRecord],
    top_n: Optional[int] = None,
) -> ParsedRecommendationResult:
    top_n = top_n if top_n is not None else settings.top_n
    sorted_candidates = sorted(candidates, key=lambda r: (-r.rating, r.id))
    seen_keys: set[tuple[str, str]] = set()
    unique: list[RestaurantRecord] = []
    for r in sorted_candidates:
        key = (r.name.lower(), str(r.attributes.get("area", "")).lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(r)
        if len(unique) >= top_n:
            break

    items = [
        LLMRecommendationItem(
            rank=i + 1,
            restaurant_id=r.id,
            name=r.name,
            explanation=_template_explanation(prefs),
        )
        for i, r in enumerate(unique)
    ]
    return ParsedRecommendationResult(
        summary=None,
        recommendations=items,
        fallback_used=True,
    )


def parse_recommendation_response(
    raw: str,
    candidates: list[RestaurantRecord],
    prefs: UserPreferences,
    top_n: Optional[int] = None,
) -> ParsedRecommendationResult:
    top_n = top_n if top_n is not None else settings.top_n
    data = extract_json(raw)
    recs_raw = data.get("recommendations")
    if not isinstance(recs_raw, list) or not recs_raw:
        raise ValueError("Missing or empty recommendations array")

    by_id = _index_candidates(candidates)
    seen_ids: set[str] = set()
    items: list[LLMRecommendationItem] = []

    for entry in recs_raw:
        if not isinstance(entry, dict):
            continue
        rid = str(entry.get("restaurant_id", "")).strip()
        name = str(entry.get("name", "")).strip()
        explanation = str(entry.get("explanation", "")).strip()
        rank = entry.get("rank", len(items) + 1)

        record = by_id.get(rid)
        if record is None and name:
            record = _match_by_name(name, candidates)
            if record:
                rid = record.id
                logger.warning("Matched hallucinated id by unique name: %s", name)
            else:
                logger.warning("Dropped unknown restaurant: id=%s name=%s", rid, name)
                continue

        if rid in seen_ids:
            continue
        seen_ids.add(rid)

        if not explanation:
            explanation = _template_explanation(prefs)

        items.append(
            LLMRecommendationItem(
                rank=int(rank) if rank is not None else len(items) + 1,
                restaurant_id=rid,
                name=record.name if record else name,
                explanation=explanation,
            )
        )
        if len(items) >= top_n:
            break

    if not items:
        raise ValueError("No valid recommendations after validation")

    items.sort(key=lambda x: x.rank)
    renumbered = [
        LLMRecommendationItem(
            rank=i + 1,
            restaurant_id=item.restaurant_id,
            name=item.name,
            explanation=item.explanation,
        )
        for i, item in enumerate(items)
    ]

    summary = data.get("summary")
    return ParsedRecommendationResult(
        summary=str(summary).strip() if summary else None,
        recommendations=renumbered,
        fallback_used=False,
    )
