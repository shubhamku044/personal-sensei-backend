"""Agent tools and function definitions.

Tools the LLM can call during a tutoring session. Each tool's docstring is
surfaced to the model as its description, so keep them clear and specific.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool, tool


@tool
def list_study_topics() -> list[str]:
    """List the study topics currently available to the learner."""
    return ["Python fundamentals", "Data structures", "System design"]


@tool
def get_topic_overview(topic: str) -> str:
    """Return a short overview of a study topic.

    Args:
        topic: The name of the topic to summarise.
    """
    return f"'{topic}' covers the core concepts a learner needs to get started."


# Registered with the agent in app/agent/graph.py.
TOOLS: list[BaseTool] = [list_study_topics, get_topic_overview]
