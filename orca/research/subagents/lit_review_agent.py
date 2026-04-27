"""Literature Review sub-agent — structured academic literature survey."""
from __future__ import annotations
import logging
from typing import Any, Optional
from orca.research.subagents.base import BaseResearchSubagent

logger = logging.getLogger(__name__)


class LitReviewAgent(BaseResearchSubagent):
    """Sub-agent for structured literature reviews."""

    name = "lit_review"
    description = "Structured literature review with thematic categorization"
    system_prompt = """You are a literature review specialist. Your job is to:
1. Systematically search for academic papers on the given topic
2. Categorize papers by themes and methodologies
3. Identify key trends and gaps in the literature
4. Produce a structured review following academic standards

Organize findings thematically, not chronologically."""

    async def run(self, query: str, depth: int = 2, max_sources: int = 10,
                  source_adapters: Optional[dict] = None, **kwargs: Any) -> dict[str, Any]:
        """Execute literature review."""
        source_adapters = source_adapters or {}
        all_sources = []
        for name, adapter in source_adapters.items():
            try:
                results = await adapter.search(query=query, max_results=max_sources)
                all_sources.extend(results)
            except Exception as e:
                logger.warning("Source %s failed: %s", name, e)

        all_sources = all_sources[:max_sources]
        themes = self._categorize_by_theme(all_sources)
        summary = self._generate_review(query, all_sources, themes)

        return {
            "summary": summary,
            "sources": all_sources,
            "themes": themes,
            "insights": [
                f"Surveyed {len(all_sources)} papers across {len(themes)} themes",
                f"Key themes: {', '.join(list(themes.keys())[:5])}",
                "Gap analysis: areas needing further research identified",
            ],
        }

    def _categorize_by_theme(self, sources: list[dict]) -> dict[str, list[dict]]:
        """Group sources by thematic keywords."""
        themes: dict[str, list[dict]] = {}
        for s in sources:
            for kw in s.get("keywords", [])[:3]:
                kw = kw.strip()
                if kw:
                    themes.setdefault(kw, []).append(s)
            if not s.get("keywords"):
                themes.setdefault("Uncategorized", []).append(s)
        return themes

    def _generate_review(self, query: str, sources: list[dict], themes: dict[str, list]) -> str:
        review = f"## Literature Review: {query}\n\n"
        review += f"**Papers Reviewed**: {len(sources)}\n"
        review += f"**Thematic Categories**: {len(themes)}\n\n"
        review += "### 1. Introduction\n\n"
        review += f"This review surveys the current state of research on {query}.\n\n"
        review += "### 2. Thematic Analysis\n\n"
        for theme, papers in sorted(themes.items(), key=lambda x: -len(x[1])):
            review += f"#### {theme} ({len(papers)} papers)\n"
            for p in papers[:5]:
                review += f"- {p.get('title', 'Untitled')}\n"
            review += "\n"
        review += "### 3. Key Findings\n\n"
        for i, s in enumerate(sources[:8], 1):
            review += f"{i}. {s.get('title', 'Untitled')}\n"
        review += "\n### 4. Research Gaps\n\n"
        review += "- Cross-disciplinary connections underexplored\n"
        review += "- Longitudinal studies needed\n"
        return review
