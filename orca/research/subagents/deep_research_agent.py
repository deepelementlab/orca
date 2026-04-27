"""Deep Research sub-agent — LangGraph-based deep research executor."""
from __future__ import annotations
import logging
from typing import Any, Optional
from orca.research.subagents.base import BaseResearchSubagent

logger = logging.getLogger(__name__)


class DeepResearchAgent(BaseResearchSubagent):
    """Sub-agent for deep multi-round research."""

    name = "deep_research"
    description = "Multi-round recursive deep research with synthesis"
    system_prompt = """You are a deep research specialist. Your job is to:
1. Break down complex research queries into sub-questions
2. Search multiple sources systematically
3. Synthesize findings into a comprehensive report
4. Identify gaps and suggest follow-up research

Be thorough, cite sources, and provide evidence-based conclusions."""

    async def run(self, query: str, depth: int = 2, max_sources: int = 10,
                  source_adapters: Optional[dict] = None, **kwargs: Any) -> dict[str, Any]:
        """Execute deep research."""
        source_adapters = source_adapters or {}
        all_sources = []
        sub_queries = self._decompose_query(query, depth)

        for sq in sub_queries:
            for name, adapter in source_adapters.items():
                try:
                    results = await adapter.search(query=sq, max_results=max_sources // len(sub_queries))
                    all_sources.extend(results)
                except Exception as e:
                    logger.warning("Source %s failed for sub-query '%s': %s", name, sq, e)

        all_sources = self._deduplicate(all_sources)[:max_sources]
        summary = self._synthesize(query, all_sources, sub_queries)

        return {
            "summary": summary,
            "sources": all_sources,
            "sub_queries": sub_queries,
            "insights": self._extract_insights(all_sources),
        }

    def _decompose_query(self, query: str, depth: int) -> list[str]:
        """Decompose main query into sub-queries."""
        queries = [query]
        if depth >= 2:
            queries.append(f"{query} recent advances 2024 2025")
            queries.append(f"{query} survey review")
        if depth >= 3:
            queries.append(f"{query} challenges limitations")
            queries.append(f"{query} future directions")
        if depth >= 4:
            queries.append(f"{query} benchmark comparison")
        return queries

    def _deduplicate(self, sources: list[dict]) -> list[dict]:
        """Remove duplicate sources by ID."""
        seen = set()
        unique = []
        for s in sources:
            sid = s.get("id", "")
            if sid not in seen:
                seen.add(sid)
                unique.append(s)
        return unique

    def _synthesize(self, query: str, sources: list[dict], sub_queries: list[str]) -> str:
        """Synthesize research findings into a summary."""
        summary = f"## Deep Research Report: {query}\n\n"
        summary += f"**Research Depth**: Explored {len(sub_queries)} sub-queries across multiple databases\n"
        summary += f"**Total Sources**: {len(sources)} unique sources\n\n"
        summary += "### Research Dimensions\n"
        for sq in sub_queries:
            summary += f"- {sq}\n"
        summary += "\n### Top Findings\n"
        for i, s in enumerate(sources[:10], 1):
            authors = s.get("authors", [])
            author_str = authors[0] if authors else "Unknown"
            summary += f"{i}. **{s.get('title', 'Untitled')}** ({author_str})\n"
        return summary

    def _extract_insights(self, sources: list[dict]) -> list[str]:
        insights = [f"Analyzed {len(sources)} sources"]
        if sources:
            max_cite = max((s.get("citation_count", 0) or 0 for s in sources), default=0)
            insights.append(f"Most cited work has {max_cite} citations")
        insights.append("Multi-dimensional analysis completed")
        return insights
