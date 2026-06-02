"""Domain models (Phase 1–2)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class BudgetBucket(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


BUDGET_SYNONYMS: dict[str, BudgetBucket] = {
    "low": BudgetBucket.LOW,
    "cheap": BudgetBucket.LOW,
    "affordable": BudgetBucket.LOW,
    "medium": BudgetBucket.MEDIUM,
    "moderate": BudgetBucket.MEDIUM,
    "mid": BudgetBucket.MEDIUM,
    "high": BudgetBucket.HIGH,
    "expensive": BudgetBucket.HIGH,
    "premium": BudgetBucket.HIGH,
}


class RestaurantRecord(BaseModel):
    """Canonical restaurant record after normalization."""

    id: str
    name: str
    location: str  # city (e.g. Bangalore), normalized
    cuisines: list[str]
    rating: float
    cost_for_two: Optional[float] = None
    cost_bucket: Optional[BudgetBucket] = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class UserPreferences(BaseModel):
    """User search preferences for structured filtering."""

    location: str
    budget: BudgetBucket
    cuisine: str
    min_rating: float = Field(ge=0.0, le=5.0)
    additional_notes: Optional[str] = None

    @field_validator("location", "cuisine")
    @classmethod
    def strip_required(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("must not be empty")
        return text

    @field_validator("additional_notes")
    @classmethod
    def strip_notes(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = value.strip()
        return text or None

    @classmethod
    def parse_budget(cls, raw: str) -> BudgetBucket:
        key = raw.strip().lower()
        if key not in BUDGET_SYNONYMS:
            raise ValueError(f"Invalid budget '{raw}'. Use: low, medium, or high.")
        return BUDGET_SYNONYMS[key]


class FilterResult(BaseModel):
    """Outcome of structured filtering (before LLM)."""

    candidates: list[RestaurantRecord] = Field(default_factory=list)
    total_matched: int = 0
    capped: bool = False
    message: Optional[str] = None
    reason_code: Optional[str] = None

    @property
    def is_empty(self) -> bool:
        return len(self.candidates) == 0
