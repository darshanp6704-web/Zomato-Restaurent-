"""LLM clients: Groq (production) and mock (tests)."""

from __future__ import annotations

import json
import logging
import time
from typing import Optional, Protocol

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


class GroqClient:
    """Groq chat completions via official SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.groq_api_key
        self.model = model if model is not None else settings.groq_model
        self.temperature = (
            temperature if temperature is not None else settings.llm_temperature
        )

    def complete(self, messages: list[dict[str, str]]) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set")

        from groq import Groq

        client = Groq(api_key=self.api_key)
        last_error: Optional[Exception] = None
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
                content = response.choices[0].message.content
                if not content or not str(content).strip():
                    raise ValueError("Empty response from Groq")
                return str(content).strip()
            except Exception as exc:
                last_error = exc
                err_str = str(exc).lower()
                if attempt == 0 and ("429" in err_str or "rate" in err_str):
                    logger.warning("Groq rate limit; retrying in 2s...")
                    time.sleep(2)
                    continue
                raise
        raise last_error  # type: ignore[misc]


class MockLLMClient:
    """Returns fixed JSON for unit tests."""

    def __init__(self, response_json: Optional[dict] = None) -> None:
        self.response_json = response_json or {
            "summary": "Mock summary for testing.",
            "recommendations": [
                {
                    "rank": 1,
                    "restaurant_id": "r1",
                    "name": "Italian Place",
                    "explanation": "Great Italian match for your preferences.",
                }
            ],
        }

    def complete(self, messages: list[dict[str, str]]) -> str:
        return json.dumps(self.response_json)


def get_llm_client() -> Optional[LLMClient]:
    if settings.groq_api_key:
        return GroqClient()
    return None
