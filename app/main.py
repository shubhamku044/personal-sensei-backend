"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import health
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import register_middleware


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    configure_logging()
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version=settings.version)
    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(health.router)

    get_logger(__name__).info("Application initialised (environment=%s)", settings.environment)
    return app


app = create_app()
