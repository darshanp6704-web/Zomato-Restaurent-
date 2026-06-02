"""Tests for LLM prompt builder (Phase 6)."""

from __future__ import annotations

from domain.models import BudgetBucket, UserPreferences
from llm.prompts import build_messages
from tests.fixtures.restaurants import FIXTURE_RESTAURANTS


def test_build_messages_structure():
    prefs = UserPreferences(
        location="Bangalore",
        budget=BudgetBucket.MEDIUM,
        cuisine="italian",
        min_rating=4.0,
        additional_notes="family-friendly",
    )
    candidates = FIXTURE_RESTAURANTS[:2]
    top_n = 5

    messages = build_messages(prefs, candidates, top_n)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    system_content = messages[0]["content"]
    assert "CANDIDATES" in system_content
    assert "restaurant recommendation assistant" in system_content

    user_content = messages[1]["content"]
    assert "Bangalore" in user_content
    assert "medium" in user_content
    assert "italian" in user_content
    assert "4.0" in user_content
    assert "family-friendly" in user_content
    assert "Candidates:" in user_content

    # Check serialized candidates details inside the user prompt content
    assert "Italian Place" in user_content
    assert "Budget Chinese" in user_content


def test_build_messages_no_notes():
    # Omit notes test
    prefs_no_notes = UserPreferences(
        location="Bangalore",
        budget=BudgetBucket.MEDIUM,
        cuisine="italian",
        min_rating=4.0,
        additional_notes=None,
    )
    candidates = FIXTURE_RESTAURANTS[:1]
    messages_no_notes = build_messages(prefs_no_notes, candidates, 5)
    assert "Additional notes: None" in messages_no_notes[1]["content"]
