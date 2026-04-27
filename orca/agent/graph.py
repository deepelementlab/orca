"""LangGraph agent graph definition for Orca."""
from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from orca.agent.nodes.route_to_research import route_to_research
from orca.agent.nodes.research_agent import research_agent_node

logger = logging.getLogger(__name__)

ORCA_SYSTEM_PROMPT = """You are Orca, an omniscient research assistant built by fusing DeerFlow and Feynman.
You help users with:
- Deep research on any topic
- Literature reviews
- Paper audits and peer reviews
- Source comparisons
- Paper writing assistance
- Experiment replication guidance
- Simplified explanations (ELI5)
- Session search through past research

When a user asks a research-related question, use the research tools available.
For general conversation, respond helpfully."""


async def general_agent_node(state: dict) -> dict:
    """Handle general (non-research) conversations."""
    from langchain_core.messages import HumanMessage

    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        content = getattr(last_msg, "content", str(last_msg))
        response = f"I received your message. Let me help you with that."
    else:
        response = "Hello! I am Orca, your research assistant. How can I help?"

    return {"messages": [AIMessage(content=response)]}


def make_lead_agent():
    """Create the lead Orca agent graph."""
    graph = StateGraph(dict)

    # Add nodes
    graph.add_node("router", route_to_research)
    graph.add_node("research", research_agent_node)
    graph.add_node("general", general_agent_node)

    # Set entry point
    graph.set_entry_point("router")

    # Add conditional edges
    graph.add_conditional_edges(
        "router",
        lambda state: "research" if state.get("intent") == "research" else "general",
        {"research": "research", "general": "general"},
    )

    # Both terminal nodes go to END
    graph.add_edge("research", END)
    graph.add_edge("general", END)

    return graph.compile()


# Module-level agent instance for LangGraph
agent = make_lead_agent()
