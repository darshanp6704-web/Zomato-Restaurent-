"""LLM recommendation result models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class LLMRecommendationItem(BaseModel):
    rank: int
    restaurant_id: str
    name: str
    explanation: str


class ParsedRecommendationResult(BaseModel):
    summary: Optional[str] = None
    recommendations: list[LLMRecommendationItem] = Field(default_factory=list)
    fallback_used: bool = False
