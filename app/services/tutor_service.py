"""Business logic for the tutor conversation flow."""

from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.agent.graph import build_agent
from app.core.errors import ExternalServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class TutorService:
    """Coordinates tutoring conversations on top of the LangGraph agent."""

    async def ask(self, question: str) -> str:
        """Send a learner question to the agent and return its reply.

        Args:
            question: The learner's message.

        Raises:
            ExternalServiceError: If the agent/LLM call fails.
        """
        agent = build_agent()
        try:
            result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
        except Exception as exc:
            logger.exception("agent invocation failed")
            raise ExternalServiceError from exc

        messages = result["messages"]
        return str(messages[-1].content)
