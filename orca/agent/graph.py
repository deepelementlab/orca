"""LangGraph agent graph definition for Orca."""
from __future__ import annotations

import logging

from langchain_core.messages import AIMessage
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
For general conversation, respond helpfully and knowledgeably."""


async def general_agent_node(state: dict) -> dict:
    """Handle general (non-research) conversations using LLM."""
    try:
        from orca.config.orca_config import OrcaConfig
        from orca.llm.service import LLMService

        config = OrcaConfig()
        if config.llm.api_key:
            llm = LLMService(config.llm)
            messages = state.get("messages", [])
            history = messages[:-1] if len(messages) > 1 else []
            last_content = ""
            if messages:
                last_msg = messages[-1]
                last_content = getattr(last_msg, "content", str(last_msg))
            response = await llm.invoke(ORCA_SYSTEM_PROMPT, last_content, history=history)
            return {"messages": [AIMessage(content=response)]}
    except Exception as e:
        logger.warning("LLM unavailable for general agent: %s", e)

    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        content = getattr(last_msg, "content", str(last_msg))
        response = f"I received your message: \"{content[:100]}\". Let me help you with that. You can also ask me to do research on any topic!"
    else:
        response = "Hello! I am Orca, your research assistant. How can I help?"

    return {"messages": [AIMessage(content=response)]}


def _passthrough_node(state: dict) -> dict:
    return state


def make_lead_agent():
    """Create the lead Orca agent graph."""
    graph = StateGraph(dict)

    graph.add_node("router", _passthrough_node)
    graph.add_node("research", research_agent_node)
    graph.add_node("general", general_agent_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_to_research,
        {"research": "research", "general": "general"},
    )

    graph.add_edge("research", END)
    graph.add_edge("general", END)

    return graph.compile()


agent = make_lead_agent()
