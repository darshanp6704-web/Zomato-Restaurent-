"""Integration tests for the end-to-end recommendation pipeline."""

from __future__ import annotations

import pytest

from app.pipeline import run_recommendation_pipeline
from domain.models import BudgetBucket, UserPreferences
from llm.client import MockLLMClient
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


def test_pipeline_happy_path():
    mock_client = MockLLMClient(
        {
            "summary": "Top Italian recommendations in Bangalore.",
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "r1",
                    "name": "Italian Place",
                    "explanation": "Highly recommended authentic Italian food.",
                }
            ],
        }
    )

    result = run_recommendation_pipeline(
        _prefs(),
        records=FIXTURE_RESTAURANTS,
        client=mock_client,
    )

    assert not result.filter_result.is_empty
    assert result.presentation is not None
    assert not result.presentation.fallback_used
    assert result.presentation.summary == "Top Italian recommendations in Bangalore."
    assert len(result.presentation.recommendations) == 1
    assert result.presentation.recommendations[0].name == "Italian Place"
    assert (
        result.presentation.recommendations[0].explanation
        == "Highly recommended authentic Italian food."
    )


def test_pipeline_empty_filters_never_calls_llm():
    class AssertingMockClient:
        def complete(self, messages):
            pytest.fail("LLM client should not be called when filter result is empty.")

    # Prefs matching no restaurants
    prefs = _prefs(location="Nonexistent City")

    result = run_recommendation_pipeline(
        prefs,
        records=FIXTURE_RESTAURANTS,
        client=AssertingMockClient(),
    )

    assert result.filter_result.is_empty
    assert result.presentation is None


def test_pipeline_llm_failure_triggers_fallback():
    class FailingMockClient:
        def complete(self, messages):
            raise RuntimeError("API failure")

    result = run_recommendation_pipeline(
        _prefs(budget=BudgetBucket.MEDIUM),
        records=FIXTURE_RESTAURANTS,
        client=FailingMockClient(),
    )

    assert not result.filter_result.is_empty
    assert result.presentation is not None
    assert result.presentation.fallback_used
    # Verification of fallback contents: r1 is the only medium restaurant matching 4.5 rating
    assert len(result.presentation.recommendations) == 1
    assert result.presentation.recommendations[0].name == "Italian Place"
    assert "Highly rated match" in result.presentation.recommendations[0].explanation
