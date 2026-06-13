"""Centralised logging configuration."""

from __future__ import annotations

import logging
from logging.config import dictConfig

from app.core.config import get_settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging() -> None:
    """Configure root and uvicorn loggers. Safe to call more than once."""
    settings = get_settings()
    level = "DEBUG" if settings.environment == "development" else "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": _LOG_FORMAT, "datefmt": _DATE_FORMAT},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"handlers": ["console"], "level": level},
            "loggers": {
                **{
                    name: {"handlers": ["console"], "level": level, "propagate": False}
                    for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
                },
                # Chatty third-party libraries: keep them at WARNING even in dev.
                **{
                    name: {"level": "WARNING", "propagate": True}
                    for name in ("asyncio", "httpx", "httpcore")
                },
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger. Use `get_logger(__name__)`."""
    return logging.getLogger(name)
