"""Shared rendering for CLI and Streamlit."""

from __future__ import annotations

from presentation.models import PresentationResult, RecommendationView


def render_recommendation_text(view: RecommendationView) -> str:
    area = f" ({view.area})" if view.area else ""
    lines = [
        f"{view.rank}. {view.name}{area}",
        f"   Cuisine: {view.cuisine}",
        f"   Rating: {view.rating} | Cost: {view.estimated_cost}",
        f"   Why: {view.explanation}",
    ]
    return "\n".join(lines)


def render_presentation_text(result: PresentationResult) -> str:
    parts: list[str] = []
    if result.fallback_used:
        parts.append(
            "Note: AI recommendations unavailable — showing top-rated matches.\n"
        )
    if result.summary:
        parts.append(result.summary.strip())
        parts.append("")
    for view in result.recommendations:
        parts.append(render_recommendation_text(view))
        parts.append("")
    return "\n".join(parts).strip()
