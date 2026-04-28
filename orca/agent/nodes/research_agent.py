"""Research agent node for LangGraph graph."""
from __future__ import annotations
import logging
from langchain_core.messages import AIMessage
from orca.research.engine import ResearchEngine

logger = logging.getLogger(__name__)

_engine: ResearchEngine | None = None

async def _get_engine() -> ResearchEngine:
    global _engine
    if _engine is None:
        _engine = ResearchEngine()
        await _engine.initialize()
    return _engine

async def research_agent_node(state: dict) -> dict:
    """Execute research based on the query."""
    messages = state.get("messages", [])
    if not messages:
        return {"messages": [AIMessage(content="No query provided for research.")]}

    query = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
    research_cfg = state.get("research", {}) or {}
    workflow = research_cfg.get("research_workflow", "deep_research")
    depth = research_cfg.get("research_depth", 2)
    max_sources = research_cfg.get("research_max_sources", 10)

    try:
        engine = await _get_engine()
        result = await engine.execute(workflow=workflow, query=query,
                                      depth=depth, max_sources=max_sources)
        if result.error:
            return {"messages": [AIMessage(content=f"Research error: {result.error}")],
                    "research": {**research_cfg, "research_result": None}}

        response = result.summary
        if result.sources:
            response += f"\n\n*Based on {len(result.sources)} sources*"

        return {"messages": [AIMessage(content=response)],
                "research": {**research_cfg, "research_result": result.to_dict()}}
    except Exception as e:
        logger.exception("Research agent node failed")
        return {"messages": [AIMessage(content=f"Research failed: {e}")]}
