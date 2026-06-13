"""Top-level, versioned API router.

All route modules are mounted here under the ``/api/v1`` prefix so the HTTP
surface has a single, consistent entry point.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
