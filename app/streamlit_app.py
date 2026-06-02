"""Streamlit UI for restaurant recommendations (Decoupled REST Client)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.logging_config import configure_logging
from config.settings import settings

configure_logging()
logger = logging.getLogger(__name__)

API_BASE_URL = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="Restaurant Recommendations",
    page_icon="🍽️",
    layout="centered",
)

st.title("🍽️ Restaurant Recommendations")
st.caption("Zomato dataset · Decoupled REST Client · Groq AI explanations")


def fetch_api_data(endpoint: str):
    """Helper to fetch data from backend REST API with fail-safe error handling."""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error("API error for %s: Status %d", endpoint, response.status_code)
            return None
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to FastAPI backend at %s", API_BASE_URL)
        return None


# Eager API health and data fetch at startup
unique_locations = fetch_api_data("locations")
unique_cuisines = fetch_api_data("cuisines")

# Display a prominent warning if the FastAPI backend is not running
if unique_locations is None or unique_cuisines is None:
    st.error(
        "🚨 **FastAPI REST API Backend Offline**\n\n"
        "The frontend is unable to connect to the backend server at `http://localhost:8000`.\n\n"
        "Please start the backend REST API in a separate terminal using:\n"
        "```bash\n"
        "make run-backend\n"
        "```\n"
        "Then refresh this page."
    )
    st.stop()

with st.form("preferences_form"):
    location = st.selectbox(
        "Location",
        options=unique_locations,
        index=(
            unique_locations.index("Bangalore")
            if "Bangalore" in unique_locations
            else 0
        ),
    )
    budget = st.selectbox("Budget", options=["low", "medium", "high"], index=1)

    # We can use a text input or a selectbox from unique cuisines
    cuisine_input = st.selectbox(
        "Cuisine",
        options=unique_cuisines,
        index=(unique_cuisines.index("Italian") if "Italian" in unique_cuisines else 0),
    )

    min_rating = st.slider(
        "Minimum rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1
    )
    notes = st.text_area(
        "Additional preferences (optional)",
        placeholder="e.g. family-friendly, quick service",
        height=80,
    )
    submitted = st.form_submit_button("Get recommendations", type="primary")

if submitted:
    # Prepare preferences JSON payload
    payload = {
        "location": location,
        "budget": budget,
        "cuisine": cuisine_input.lower(),  # canonical lowercase
        "min_rating": float(min_rating),
        "additional_notes": notes or None,
    }

    with st.spinner("Finding the best restaurants for you..."):
        try:
            response = requests.post(
                f"{API_BASE_URL}/recommend",
                json=payload,
                timeout=30,  # Allow time for Groq API calls
            )

            if response.status_code == 200:
                pres = response.json()

                # Check for empty state representation in JSON
                if not pres.get("recommendations"):
                    st.warning(pres.get("summary") or "No matching restaurants found.")
                else:
                    if pres.get("fallback_used"):
                        st.info(
                            "AI recommendations unavailable — showing top-rated matches. "
                            "Set `GROQ_API_KEY` in `.env` for personalized explanations."
                        )

                    if pres.get("summary"):
                        st.markdown(f"**Summary:** {pres['summary']}")

                    st.subheader("Top recommendations")
                    for view in pres["recommendations"]:
                        area = f" · {view['area']}" if view.get("area") else ""
                        st.markdown(f"### {view['rank']}. {view['name']}{area}")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Rating", f"{view['rating']}")
                        col2.write(f"**Cuisine:** {view['cuisine']}")
                        col3.write(f"**Cost:** {view['estimated_cost']}")
                        st.markdown(f"**Why this pick:** {view['explanation']}")
                        st.divider()

                    if settings.debug and pres.get("debug_info"):
                        with st.expander("Debug info"):
                            st.json(pres["debug_info"])
            else:
                st.error(
                    f"Backend API returned an error (Status {response.status_code}). "
                    "Please check the backend console logs."
                )
        except requests.exceptions.ConnectionError:
            st.error(
                "Connection lost to FastAPI backend. Please check the backend server."
            )
        except Exception as exc:
            st.error("Something went wrong. Please try again.")
            if settings.debug:
                st.exception(exc)
