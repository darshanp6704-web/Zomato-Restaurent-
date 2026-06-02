"""Stable error / reason codes for filtering and UI (see docs/edge-case.md)."""

from __future__ import annotations

from enum import Enum


class FilterReasonCode(str, Enum):
    NO_MATCHES = "ERR_NO_MATCHES"


EMPTY_FILTER_MESSAGE = """No restaurants match your preferences in our dataset.

Try:
• A nearby city or broader area name
• A more common cuisine in that city
• A lower minimum rating
• A different budget (low / medium / high)"""
