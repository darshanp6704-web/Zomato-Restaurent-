"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
NORMALIZED_CACHE_FILE = CACHE_DIR / "restaurants.parquet"


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).lower() == "true"


@dataclass(frozen=True)
class Settings:
    dataset_id: str = os.getenv(
        "DATASET_ID", "ManikaSaini/zomato-restaurant-recommendation"
    )
    dataset_split: str = os.getenv("DATASET_SPLIT", "train")
    cache_dir: Path = CACHE_DIR
    normalized_cache_file: Path = NORMALIZED_CACHE_FILE
    budget_low_max: float = float(os.getenv("BUDGET_LOW_MAX", "400"))
    budget_medium_max: float = float(os.getenv("BUDGET_MEDIUM_MAX", "550"))
    refresh_dataset: bool = _env_bool("REFRESH_DATASET")
    max_candidates: int = int(os.getenv("MAX_CANDIDATES", "40"))
    top_n: int = int(os.getenv("TOP_N", "5"))
    location_match_mode: str = os.getenv("LOCATION_MATCH_MODE", "contains")
    include_unknown_cost_in_budget: bool = _env_bool("INCLUDE_UNKNOWN_COST_IN_BUDGET")
    # Groq LLM (Phase 3+)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "") or os.getenv("LLM_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile") or os.getenv(
        "LLM_MODEL", "llama-3.3-70b-versatile"
    )
    groq_base_url: str = os.getenv(
        "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
    )
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    debug: bool = _env_bool("DEBUG")
    max_additional_notes_length: int = int(os.getenv("MAX_ADDITIONAL_NOTES_LENGTH", "500"))


settings = Settings()
