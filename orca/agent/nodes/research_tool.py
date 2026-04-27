"""Research workflow tool for LangGraph agent."""
from __future__ import annotations
import logging
from typing import Any, Optional
from langchain_core.tools import tool
from orca.research.engine import ResearchEngine

logger = logging.getLogger(__name__)

_engine: Optional[ResearchEngine] = None

async def _get_engine() -> ResearchEngine:
    global _engine
    if _engine is None:
        _engine = ResearchEngine()
        await _engine.initialize()
    return _engine

@tool
async def research_workflow(
    workflow: str,
    query: str,
    depth: int = 2,
    max_sources: int = 10,
    output_format: str = "markdown",
) -> str:
    """Execute a research workflow. Available workflows: deep_research, lit_review, paper_audit,
    source_compare, peer_review, paper_writing, replication, eli5, session_search."""
    engine = await _get_engine()
    result = await engine.execute(workflow=workflow, query=query, depth=depth,
                                  max_sources=max_sources, output_format=output_format)
    if result.error:
        return f"Error: {result.error}"
    return result.summary

@tool
async def search_papers(query: str, max_results: int = 10) -> str:
    """Search for academic papers across multiple databases."""
    engine = await _get_engine()
    results = await engine.search_sources(query=query, max_results=max_results)
    if not results:
        return "No papers found."
    output = f"Found {len(results)} papers:\n\n"
    for i, r in enumerate(results, 1):
        output += f"{i}. **{r.get('title','Untitled')}** ({r.get('source_type','')})\n"
        if r.get('authors'):
            output += f"   Authors: {', '.join(r['authors'][:3])}\n"
        if r.get('citation_count'):
            output += f"   Citations: {r['citation_count']}\n"
        output += "\n"
    return output
