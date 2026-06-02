"""End-to-end recommendation pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from data.loader import load_restaurants
from domain.filters import filter_restaurants
from domain.models import FilterResult, RestaurantRecord, UserPreferences
from llm.client import LLMClient
from llm.service import recommend
from presentation.formatter import format_presentation
from presentation.models import PresentationResult

logger = logging.getLogger(__name__)

_restaurant_cache: Optional[list[RestaurantRecord]] = None


def get_restaurants(*, refresh: bool = False) -> list[RestaurantRecord]:
    global _restaurant_cache
    if _restaurant_cache is None or refresh:
        logger.info("Loading restaurant dataset...")
        _restaurant_cache = load_restaurants(refresh=refresh)
    return _restaurant_cache


def clear_restaurant_cache() -> None:
    global _restaurant_cache
    _restaurant_cache = None


@dataclass
class PipelineResult:
    filter_result: FilterResult
    presentation: Optional[PresentationResult] = None


def run_recommendation_pipeline(
    prefs: UserPreferences,
    *,
    records: Optional[list[RestaurantRecord]] = None,
    client: Optional[LLMClient] = None,
) -> PipelineResult:
    records = records if records is not None else get_restaurants()
    filter_result = filter_restaurants(prefs, records)

    if filter_result.is_empty:
        return PipelineResult(filter_result=filter_result, presentation=None)

    llm_result = recommend(prefs, filter_result.candidates, client=client)
    presentation = format_presentation(llm_result, filter_result.candidates)
    return PipelineResult(filter_result=filter_result, presentation=presentation)
