"""Tests for LLM response parsing."""

from __future__ import annotations

import json

import pytest

from domain.models import BudgetBucket, UserPreferences
from llm.client import MockLLMClient
from llm.parser import (
    build_fallback_result,
    extract_json,
    parse_recommendation_response,
)
from llm.service import recommend
from tests.fixtures.restaurants import FIXTURE_RESTAURANTS


def _prefs() -> UserPreferences:
    return UserPreferences(
        location="Bangalore",
        budget=BudgetBucket.MEDIUM,
        cuisine="italian",
        min_rating=3.5,
    )


def test_extract_json_from_markdown_fence():
    raw = 'Here you go:\n```json\n{"recommendations": [{"rank": 1}]}\n```'
    data = extract_json(raw)
    assert "recommendations" in data


def test_parse_valid_response():
    raw = json.dumps(
        {
            "summary": "Great Italian spots.",
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "r1",
                    "name": "Italian Place",
                    "explanation": "Matches your Italian craving.",
                }
            ],
        }
    )
    result = parse_recommendation_response(raw, FIXTURE_RESTAURANTS, _prefs(), top_n=5)
    assert result.summary == "Great Italian spots."
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "r1"
    assert not result.fallback_used


def test_parse_drops_unknown_id():
    raw = json.dumps(
        {
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "fake",
                    "name": "Ghost",
                    "explanation": "Nope",
                },
                {
                    "rank": 2,
                    "restaurant_id": "r1",
                    "name": "Italian Place",
                    "explanation": "Yes",
                },
            ]
        }
    )
    result = parse_recommendation_response(raw, FIXTURE_RESTAURANTS, _prefs(), top_n=5)
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "r1"


def test_parse_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_recommendation_response("not json", FIXTURE_RESTAURANTS, _prefs())


def test_fallback_result():
    candidates = [FIXTURE_RESTAURANTS[0], FIXTURE_RESTAURANTS[2]]
    result = build_fallback_result(_prefs(), candidates, top_n=2)
    assert result.fallback_used
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_id == "r3"  # higher rating


def test_recommend_with_mock_client():
    mock = MockLLMClient(
        {
            "summary": "Mock picks",
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "r1",
                    "name": "Italian Place",
                    "explanation": "Test explanation",
                }
            ],
        }
    )
    filtered = [FIXTURE_RESTAURANTS[0], FIXTURE_RESTAURANTS[2]]
    result = recommend(_prefs(), filtered, client=mock)
    assert result.recommendations[0].explanation == "Test explanation"
