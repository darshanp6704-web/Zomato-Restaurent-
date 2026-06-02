"""Build user-facing recommendation views from LLM + restaurant records."""

from __future__ import annotations

import logging
from typing import Optional

from config.settings import settings
from domain.models import RestaurantRecord
from llm.models import ParsedRecommendationResult
from presentation.models import PresentationResult, RecommendationView

logger = logging.getLogger(__name__)


def _title_cuisine(cuisines: list[str]) -> str:
    if not cuisines:
        return "Cuisine not listed"
    return ", ".join(c.strip().title() for c in cuisines if c.strip())


def format_estimated_cost(record: RestaurantRecord) -> str:
    if record.cost_for_two is not None:
        return f"₹{record.cost_for_two:.0f} for two"
    if record.cost_bucket is not None:
        return f"{record.cost_bucket.value.title()} budget"
    return "Cost not available"


def format_recommendation_view(
    item_rank: int,
    record: RestaurantRecord,
    explanation: str,
) -> RecommendationView:
    return RecommendationView(
        rank=item_rank,
        name=record.name,
        cuisine=_title_cuisine(record.cuisines),
        rating=round(record.rating, 1),
        estimated_cost=format_estimated_cost(record),
        explanation=explanation,
        location=record.location,
        area=record.attributes.get("area"),
    )


def format_presentation(
    llm_result: ParsedRecommendationResult,
    candidates: list[RestaurantRecord],
    *,
    debug: Optional[bool] = None,
) -> PresentationResult:
    """Merge LLM output with canonical restaurant fields."""
    debug = settings.debug if debug is None else debug
    by_id = {r.id: r for r in candidates}
    views: list[RecommendationView] = []

    for item in llm_result.recommendations:
        record = by_id.get(item.restaurant_id)
        if record is None:
            logger.error("Missing record for id=%s; skipping", item.restaurant_id)
            continue
        views.append(format_recommendation_view(item.rank, record, item.explanation))

    debug_info = None
    if debug:
        debug_info = {
            "candidate_count": len(candidates),
            "fallback_used": llm_result.fallback_used,
            "candidate_ids": [c.id for c in candidates[:10]],
        }

    return PresentationResult(
        summary=llm_result.summary,
        recommendations=views,
        fallback_used=llm_result.fallback_used,
        debug_info=debug_info,
    )
