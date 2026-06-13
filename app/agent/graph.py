"""LangGraph agent definition.

Builds a tool-calling agent (via ``langchain.agents.create_agent``, which
compiles to a LangGraph graph) backed by an OpenAI chat model and the tools
declared in ``app.agent.tools``. The graph is constructed lazily and cached so
that importing this module never requires an API key.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.agent.tools import TOOLS
from app.core.config import get_settings

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

SYSTEM_PROMPT = (
    "You are Personal Sensei, a patient and encouraging tutor. "
    "Explain concepts step by step, check the learner's understanding, and use "
    "the available tools to ground your answers. Prefer short, concrete examples."
)


@lru_cache(maxsize=1)
def build_agent() -> CompiledStateGraph[Any, Any, Any, Any]:
    """Build and cache the tutor agent graph.

    Reads model configuration from settings. The ``OPENAI_API_KEY``
    environment variable must be set for the underlying model to authenticate.
    """
    settings = get_settings()
    model = ChatOpenAI(
        model_name=settings.openai_model,
        temperature=settings.agent_temperature,
        max_tokens=settings.agent_max_tokens,
        # ``api_key`` is langchain's documented alias for the ``openai_api_key``
        # field; the pydantic mypy plugin only sees the field name, so this is a
        # false positive.
        api_key=settings.openai_api_key,  # type: ignore[call-arg]
    )
    return create_agent(model, TOOLS, system_prompt=SYSTEM_PROMPT)
