"""Automated API contract tests for FastAPI backend (Phase 6)."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app
from tests.fixtures.restaurants import FIXTURE_RESTAURANTS

client = TestClient(app)


def test_api_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "recommendation-engine",
    }


@patch("app.api.get_restaurants")
def test_api_locations(mock_get):
    mock_get.return_value = FIXTURE_RESTAURANTS

    response = client.get("/api/locations")
    assert response.status_code == 200
    locations = response.json()
    assert isinstance(locations, list)
    # Check that neighborhoods are sorted unique values from FIXTURE_RESTAURANTS
    assert "Bangalore" in locations
    assert "Delhi" in locations


@patch("app.api.get_restaurants")
def test_api_cuisines(mock_get):
    mock_get.return_value = FIXTURE_RESTAURANTS

    response = client.get("/api/cuisines")
    assert response.status_code == 200
    cuisines = response.json()
    assert isinstance(cuisines, list)
    assert "Italian" in cuisines
    assert "Chinese" in cuisines


@patch("app.api.get_restaurants")
@patch("app.api.run_recommendation_pipeline")
def test_api_recommend_happy_path(mock_run, mock_get):
    from domain.models import FilterResult
    from presentation.models import PresentationResult, RecommendationView

    mock_get.return_value = FIXTURE_RESTAURANTS
    mock_run.return_value = type(
        "Result",
        (),
        {
            "filter_result": FilterResult(
                candidates=[FIXTURE_RESTAURANTS[0]],
                total_matched=1,
                capped=False,
            ),
            "presentation": PresentationResult(
                summary="API recommend picks",
                recommendations=[
                    RecommendationView(
                        rank=1,
                        name="Italian Place",
                        cuisine="Italian",
                        rating=4.5,
                        estimated_cost="₹450 for two",
                        explanation="Great match",
                    )
                ],
                fallback_used=False,
            ),
        },
    )()

    payload = {
        "location": "Bangalore",
        "budget": "medium",
        "cuisine": "italian",
        "min_rating": 3.5,
    }

    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "API recommend picks"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["name"] == "Italian Place"
    assert not data["fallback_used"]


@patch("app.api.get_restaurants")
@patch("app.api.run_recommendation_pipeline")
def test_api_recommend_empty_filter(mock_run, mock_get):
    from domain.models import FilterResult

    mock_get.return_value = FIXTURE_RESTAURANTS
    mock_run.return_value = type(
        "Result",
        (),
        {
            "filter_result": FilterResult(
                candidates=[],
                total_matched=0,
                capped=False,
                message="No restaurants match.",
            ),
            "presentation": None,
        },
    )()

    payload = {
        "location": "Nonexistent",
        "budget": "medium",
        "cuisine": "italian",
        "min_rating": 3.5,
    }

    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "No restaurants match."
    assert len(data["recommendations"]) == 0
