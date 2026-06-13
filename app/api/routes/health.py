"""Health-check endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response payload for the health-check endpoint."""

    status: str
    app: str
    version: str
    environment: str


@router.get("/health", summary="Liveness probe")
async def health() -> HealthResponse:
    """Return the service's liveness status and basic metadata."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.version,
        environment=settings.environment,
    )
