"""LangGraph agent definition.

Builds a ReAct-style agent (LangGraph's prebuilt graph) backed by an OpenAI
chat model and the tools declared in ``app.agent.tools``. The graph is
constructed lazily and cached so that importing this module never requires an
API key.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

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
    )
    return create_react_agent(model, TOOLS, prompt=SYSTEM_PROMPT)
