"""Chat conversation endpoints."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.core.errors import AppError
from app.core.logging import get_logger
from app.services.tutor_service import TutorService

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = get_logger(__name__)
router = APIRouter(tags=["chat"])
_tutor = TutorService()


class ChatRequest(BaseModel):
    """A single learner message sent to the tutor."""

    message: str = Field(min_length=1, max_length=4000)
    thread_id: str = Field(description="Conversation id; reuse it to keep memory.")


class ChatResponse(BaseModel):
    """The tutor's reply."""

    reply: str


@router.post("/chat", summary="Send a message to the tutor agent")
async def chat(request: ChatRequest) -> ChatResponse:
    """Forward the learner's message to the agent and return its full reply."""
    reply = await _tutor.ask(request.message, thread_id=request.thread_id)
    return ChatResponse(reply=reply)


@router.post("/chat/stream", summary="Stream the tutor agent's reply (SSE)")
async def chat_stream(request: ChatRequest) -> EventSourceResponse:
    """Stream the agent's reply as Server-Sent Events.

    Emits ``token`` events with text deltas, a terminal ``done`` event, and an
    ``error`` event if generation fails.
    """

    async def event_source() -> AsyncIterator[dict[str, str]]:
        try:
            async for delta in _tutor.astream(request.message, thread_id=request.thread_id):
                yield {"data": json.dumps({"type": "token", "content": delta})}
        except AppError as exc:
            yield {"data": json.dumps({"type": "error", "message": exc.message})}
            return
        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(event_source())
