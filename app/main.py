"""CLI entry point for restaurant recommendations."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.input_validation import parse_user_preferences
from app.logging_config import configure_logging
from app.pipeline import get_restaurants, run_recommendation_pipeline
from app.renderer import render_presentation_text
from config.settings import settings

logger = logging.getLogger(__name__)


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or default


def _interactive_preferences():
    print("Restaurant Recommendation System\n")
    location = _prompt("Location (e.g. Bangalore)", "Bangalore")
    budget = _prompt("Budget (low / medium / high)", "medium")
    cuisine = _prompt("Cuisine (e.g. italian)", "italian")
    rating_raw = _prompt("Minimum rating (0–5)", "4.0")
    notes = _prompt("Additional notes (optional)", "")

    try:
        min_rating = float(rating_raw)
    except ValueError:
        return None, "Minimum rating must be a number."

    return parse_user_preferences(
        location=location,
        budget_raw=budget,
        cuisine=cuisine,
        min_rating=min_rating,
        additional_notes=notes or None,
    )


def main(argv: list[str] | None = None) -> int:
    configure_logging()

    print("Initializing system and loading restaurant database...")
    try:
        get_restaurants()
    except Exception as exc:
        print(
            "Error: Unable to load restaurant data. Check your connection and try again.",
            file=sys.stderr,
        )
        logger.error("Dataset load failed on startup: %s", exc)
        return 1

    parser = argparse.ArgumentParser(
        description="AI-powered restaurant recommendations (Groq + Zomato dataset)"
    )
    parser.add_argument("--location", help="City or area")
    parser.add_argument("--budget", help="low, medium, or high")
    parser.add_argument("--cuisine", help="Preferred cuisine")
    parser.add_argument("--min-rating", type=float, help="Minimum rating 0–5")
    parser.add_argument("--notes", default="", help="Additional preferences")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Prompt for preferences"
    )
    args = parser.parse_args(argv)

    if args.interactive or not all(
        [args.location, args.budget, args.cuisine, args.min_rating is not None]
    ):
        prefs, error = _interactive_preferences()
    else:
        prefs, error = parse_user_preferences(
            location=args.location or "",
            budget_raw=args.budget or "",
            cuisine=args.cuisine or "",
            min_rating=args.min_rating if args.min_rating is not None else 4.0,
            additional_notes=args.notes or None,
        )

    if error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    assert prefs is not None

    print("\nFinding recommendations...\n")
    try:
        result = run_recommendation_pipeline(prefs)
    except Exception as exc:
        print(f"Something went wrong. Please try again.", file=sys.stderr)
        if settings.debug:
            print(exc, file=sys.stderr)
        return 1

    if result.filter_result.is_empty:
        print(result.filter_result.message)
        return 0

    assert result.presentation is not None
    print(render_presentation_text(result.presentation))

    if settings.debug and result.presentation.debug_info:
        print("\n--- DEBUG ---")
        print(result.presentation.debug_info)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
