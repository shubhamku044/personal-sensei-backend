"""Chat conversation endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.tutor_service import TutorService

router = APIRouter(tags=["chat"])
_tutor = TutorService()


class ChatRequest(BaseModel):
    """A single learner message sent to the tutor."""

    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    """The tutor's reply."""

    reply: str


@router.post("/chat", summary="Send a message to the tutor agent")
async def chat(request: ChatRequest) -> ChatResponse:
    """Forward the learner's message to the agent and return its reply."""
    reply = await _tutor.ask(request.message)
    return ChatResponse(reply=reply)
