"""FastAPI REST API backend for restaurant recommendations."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.logging_config import configure_logging
from app.pipeline import get_restaurants, run_recommendation_pipeline
from domain.models import UserPreferences
from presentation.models import PresentationResult

# Configure structured logging
configure_logging()
logger = logging.getLogger(__name__)


import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eagerly load dataset on startup in the background to prevent blocking port binding."""
    logger.info("Initializing REST API backend...")
    
    def background_load():
        try:
            get_restaurants()
            logger.info("Background restaurant database preload completed successfully.")
        except Exception as exc:
            logger.error("Background dataset preload failed: %s", exc)

    thread = threading.Thread(target=background_load, daemon=True)
    thread.start()
    
    yield
    logger.info("Shutting down REST API backend...")


app = FastAPI(
    title="Zomato Recommendation API",
    description="Hybrid structured filter + Groq AI explanations backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for the local React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Safely allow all for local dev splits
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root_check():
    """Root health endpoint for standard cloud health checkers."""
    return {"status": "ok", "service": "recommendation-engine", "message": "Zomato AI API is active."}


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "recommendation-engine"}


@app.get("/api/locations", response_model=list[str])
def get_locations():
    """Get a sorted list of unique neighborhoods/areas in the dataset."""
    try:
        records = get_restaurants()
        unique = sorted(list(set(r.location for r in records if r.location)))
        return unique
    except Exception as exc:
        logger.error("Failed to fetch unique locations: %s", exc)
        raise HTTPException(status_code=500, detail="Unable to retrieve locations.")


@app.get("/api/cuisines", response_model=list[str])
def get_cuisines():
    """Get a sorted list of all unique cuisines in the dataset."""
    try:
        records = get_restaurants()
        unique_set = set()
        for r in records:
            for c in r.cuisines:
                if c.strip():
                    unique_set.add(c.strip().title())
        return sorted(list(unique_set))
    except Exception as exc:
        logger.error("Failed to fetch unique cuisines: %s", exc)
        raise HTTPException(status_code=500, detail="Unable to retrieve cuisines.")


@app.post("/api/recommend", response_model=PresentationResult)
def get_recommendations(prefs: UserPreferences):
    """Submit user preferences and get ranked recommendations with explanations."""
    try:
        result = run_recommendation_pipeline(prefs)
        if result.filter_result.is_empty:
            # Reconstruct an empty presentation result with a friendly explanation
            return PresentationResult(
                summary=result.filter_result.message
                or "No matching restaurants found.",
                recommendations=[],
                fallback_used=False,
                debug_info={"candidate_count": 0, "fallback_used": False},
            )
        assert result.presentation is not None
        return result.presentation
    except Exception as exc:
        logger.error("Recommendation pipeline failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating recommendations.",
        )
