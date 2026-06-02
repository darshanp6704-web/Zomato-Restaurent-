"""Tests for presentation formatter."""

from __future__ import annotations

from domain.models import BudgetBucket
from llm.models import LLMRecommendationItem, ParsedRecommendationResult
from presentation.formatter import format_estimated_cost, format_presentation
from tests.fixtures.restaurants import FIXTURE_RESTAURANTS


def test_format_estimated_cost_numeric():
    assert "800" in format_estimated_cost(FIXTURE_RESTAURANTS[2])


def test_format_estimated_cost_unknown():
    assert format_estimated_cost(FIXTURE_RESTAURANTS[4]) == "Cost not available"


def test_format_presentation_merges_fields():
    llm_result = ParsedRecommendationResult(
        summary="Summary line",
        recommendations=[
            LLMRecommendationItem(
                rank=1,
                restaurant_id="r1",
                name="Italian Place",
                explanation="Perfect Italian fit.",
            )
        ],
    )
    candidates = [FIXTURE_RESTAURANTS[0]]
    pres = format_presentation(llm_result, candidates, debug=True)

    assert pres.summary == "Summary line"
    assert len(pres.recommendations) == 1
    view = pres.recommendations[0]
    assert view.name == "Italian Place"
    assert "Italian" in view.cuisine or "italian" in view.cuisine.lower()
    assert view.rating == 4.5
    assert "450" in view.estimated_cost
    assert view.explanation == "Perfect Italian fit."
    assert view.area == "Koramangala"
    assert pres.debug_info is not None
