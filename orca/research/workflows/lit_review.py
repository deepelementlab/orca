"""Literature Review — structured literature survey."""
from __future__ import annotations

import logging
from typing import Any, Optional

from orca.models.citation import Citation
from orca.models.research import ResearchResult
from orca.models.source import Source
from orca.research.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class LitReviewWorkflow(BaseWorkflow):
    name = "lit_review"
    description = "结构化文献综述"
    category = "academic"
    prompt_template = "lit"

    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs) -> ResearchResult:
        source_adapters = source_adapters or {}
        sources_data: list[dict[str, Any]] = []
        for name, adapter in source_adapters.items():
            try:
                sources_data.extend(await adapter.search(query=query, max_results=max_sources))
            except Exception as e:
                logger.warning("Source %s: %s", name, e)

        sources = [Source.from_dict(s) for s in sources_data[:max_sources]]
        citations = [Citation(source_id=s.id, context=s.title) for s in sources]

        context = self._format_sources_for_context(sources_data)
        if self._llm:
            summary = await self._analyze_with_llm(query, context)
        else:
            summary = self._build_fallback_summary(query, sources_data)

        return ResearchResult(workflow=self.name, query=query, summary=summary,
                              sources=sources, citations=citations,
                              insights=[f"Survey covers {len(sources)} papers"],
                              confidence_score=min(0.9, 0.4 + len(sources) * 0.04))

    def _build_fallback_summary(self, query: str, sources_data: list[dict]) -> str:
        themes: set[str] = set()
        for s in sources_data[:10]:
            for kw in s.get("keywords", [])[:2]:
                themes.add(kw)
        summary = f"## Literature Review: {query}\n\nSurveyed {len(sources_data)} papers.\n\n### Themes\n"
        for t in sorted(themes)[:8]:
            summary += f"- {t}\n"
        summary += "\n### Papers\n"
        for i, s in enumerate(sources_data[:15], 1):
            summary += f"{i}. **{s.get('title', 'Untitled')}** ({s.get('published_date', 'n.d.')})\n"
        return summary
