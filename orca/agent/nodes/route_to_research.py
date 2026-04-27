"""Route to research agent — conditional edge logic."""
from __future__ import annotations
import logging
from typing import Literal

logger = logging.getLogger(__name__)

def route_to_research(state: dict) -> Literal["research", "general"]:
    """Determine if the query should be routed to research agent."""
    messages = state.get("messages", [])
    if not messages:
        return "general"

    research_state = state.get("research", {})
    if isinstance(research_state, dict) and research_state.get("intent") == "research":
        return "research"

    last_msg = messages[-1]
    content = (last_msg.content if hasattr(last_msg, "content") else str(last_msg)).lower()
    research_keywords = ["research", "论文", "文献", "survey", "deep research",
                         "literature review", "lit review", "研究", "综述",
                         "audit", "compare", "review", "replicate", "explain"]
    if any(kw in content for kw in research_keywords):
        logger.info("Routing to research agent for query: %s", content[:100])
        return "research"

    return "general"
