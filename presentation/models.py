"""Display models for formatted recommendations."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RecommendationView(BaseModel):
    rank: int
    name: str
    cuisine: str
    rating: float
    estimated_cost: str
    explanation: str
    location: Optional[str] = None
    area: Optional[str] = None


class PresentationResult(BaseModel):
    summary: Optional[str] = None
    recommendations: list[RecommendationView] = Field(default_factory=list)
    fallback_used: bool = False
    debug_info: Optional[dict] = None
