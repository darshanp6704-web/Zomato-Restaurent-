"""Orchestrate Groq recommendation with fallback."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Optional

from config.settings import settings
from domain.models import RestaurantRecord, UserPreferences
from llm.client import LLMClient, get_llm_client
from llm.models import ParsedRecommendationResult
from llm.parser import build_fallback_result, parse_recommendation_response
from llm.prompts import build_fix_json_messages, build_messages

logger = logging.getLogger(__name__)


def recommend(
    prefs: UserPreferences,
    candidates: list[RestaurantRecord],
    *,
    client: Optional[LLMClient] = None,
    top_n: Optional[int] = None,
) -> ParsedRecommendationResult:
    """
    Rank and explain candidates via Groq, with rating-based fallback on failure.
    """
    top_n = top_n if top_n is not None else settings.top_n
    if not candidates:
        logger.info("No candidates to recommend.")
        return ParsedRecommendationResult(recommendations=[], fallback_used=False)

    llm_client = client if client is not None else get_llm_client()
    if llm_client is None:
        logger.warning(
            "GROQ_API_KEY not set; using rating fallback (WARN_LLM_FALLBACK)"
        )
        fallback_res = build_fallback_result(prefs, candidates, top_n=top_n)
        logger.info(
            "Fallback rating-based recommendations returned: %d items",
            len(fallback_res.recommendations),
        )
        return fallback_res

    messages = build_messages(prefs, candidates, top_n)
    candidate_ids = [c.id for c in candidates]
    logger.info("Querying LLM with %d candidate restaurants", len(candidates))

    if settings.debug:
        prompt_content = json.dumps(messages)
        prompt_hash = hashlib.sha256(prompt_content.encode("utf-8")).hexdigest()[:8]
        logger.info(
            "[DEBUG] Prompt Hash: %s | Candidate IDs: %s",
            prompt_hash,
            candidate_ids,
        )

    start_time = time.perf_counter()
    try:
        raw = llm_client.complete(messages)
        latency = time.perf_counter() - start_time
        logger.info("LLM query completed in %.2fs", latency)

        try:
            res = parse_recommendation_response(raw, candidates, prefs, top_n=top_n)
            logger.info("LLM recommendation parsing succeeded.")
            return res
        except ValueError as parse_err:
            logger.warning("Parse failed (%s); retrying fix-json prompt", parse_err)
            fix_messages = build_fix_json_messages(raw)
            start_fix = time.perf_counter()
            raw_fixed = llm_client.complete(fix_messages)
            fix_latency = time.perf_counter() - start_fix
            logger.info("LLM fix-json query completed in %.2fs", fix_latency)
            res = parse_recommendation_response(
                raw_fixed, candidates, prefs, top_n=top_n
            )
            logger.info("LLM fix-json recommendation parsing succeeded.")
            return res
    except Exception as exc:
        latency = time.perf_counter() - start_time
        logger.error(
            "Groq recommendation failed after %.2fs: %s (WARN_LLM_FALLBACK)",
            latency,
            exc,
        )
        fallback_res = build_fallback_result(prefs, candidates, top_n=top_n)
        logger.info(
            "Fallback rating-based recommendations returned: %d items",
            len(fallback_res.recommendations),
        )
        return fallback_res
