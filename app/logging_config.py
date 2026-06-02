"""Centralized logging configuration for the recommendation system."""

from __future__ import annotations

import logging

from config.settings import settings


def configure_logging() -> None:
    """Configure clean, structured console logging for the application."""
    # Prevent duplicate configuration if already initialized
    if logging.getLogger().handlers:
        return

    level = logging.DEBUG if settings.debug else logging.INFO
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
    )

    # Silence excessively verbose external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("groq").setLevel(logging.WARNING)
    logging.getLogger("datasets").setLevel(logging.WARNING)
    logging.getLogger("filelock").setLevel(logging.WARNING)
    logging.getLogger("fsspec").setLevel(logging.WARNING)
