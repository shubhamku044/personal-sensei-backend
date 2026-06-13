"""Business logic for the tutor conversation flow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage

from app.agent.graph import build_agent
from app.core.errors import ExternalServiceError
from app.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from langchain_core.runnables import RunnableConfig

logger = get_logger(__name__)


class TutorService:
    """Coordinates tutoring conversations on top of the LangGraph agent.

    Conversation state is keyed by ``thread_id`` via the agent's checkpointer,
    so passing the same id across calls gives the agent memory of the chat.
    """

    @staticmethod
    def _config(thread_id: str) -> RunnableConfig:
        return {"configurable": {"thread_id": thread_id}}

    async def ask(self, question: str, *, thread_id: str) -> str:
        """Send a learner question to the agent and return its full reply.

        Raises:
            ExternalServiceError: If the agent/LLM call fails.
        """
        agent = build_agent()
        try:
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=question)]},
                config=self._config(thread_id),
            )
        except Exception as exc:
            logger.exception("agent invocation failed")
            raise ExternalServiceError from exc

        messages = result["messages"]
        return str(messages[-1].content)

    async def astream(self, question: str, *, thread_id: str) -> AsyncIterator[str]:
        """Stream the agent's reply token by token.

        Yields only the assistant's visible text deltas (tool-call chunks and
        intermediate steps are filtered out).

        Raises:
            ExternalServiceError: If the agent/LLM call fails.
        """
        agent = build_agent()
        try:
            async for chunk, _metadata in agent.astream(
                {"messages": [HumanMessage(content=question)]},
                config=self._config(thread_id),
                stream_mode="messages",
            ):
                content = getattr(chunk, "content", None)
                if isinstance(content, str) and content:
                    yield content
        except Exception as exc:
            logger.exception("agent streaming failed")
            raise ExternalServiceError from exc
