"""ELI5 — Explain Like I'm 5."""
from __future__ import annotations

import logging
from typing import Any, Optional

from orca.models.research import ResearchResult
from orca.models.source import Source
from orca.research.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class ELI5Workflow(BaseWorkflow):
    name = "eli5"
    description = "通俗解释 (Explain Like I'm 5)"
    category = "education"
    prompt_template = "eli5"

    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs) -> ResearchResult:
        source_adapters = source_adapters or {}
        sources_data: list[dict[str, Any]] = []
        for name, adapter in source_adapters.items():
            try:
                sources_data.extend(await adapter.search(query=query, max_results=5))
            except Exception as e:
                logger.warning("Source %s: %s", name, e)

        sources = [Source.from_dict(s) for s in sources_data[:5]]

        context = self._format_sources_for_context(sources_data)
        if self._llm:
            eli5_prompt = (self.get_system_prompt() + "\n\n"
                           "IMPORTANT: Explain in very simple terms that anyone can understand. "
                           "Use analogies and everyday examples. Avoid jargon.")
            summary = await self._llm.invoke(eli5_prompt, f"Explain simply: {query}\n\nReference material:\n{context}")
        else:
            summary = self._build_fallback_summary(query, sources_data)

        return ResearchResult(workflow=self.name, query=query, summary=summary,
                              sources=sources, insights=["Simplified explanation with analogies"],
                              confidence_score=0.8)

    def _build_fallback_summary(self, query: str, sources_data: list[dict]) -> str:
        summary = (f"## ELI5: {query}\n\n### Simple Explanation\n\n"
                   f"Imagine {query.lower()} is like a recipe:\n\n"
                   "1. **Ingredients**: The basic building blocks\n2. **Recipe**: How they come together\n3. **Result**: What you get at the end\n\n"
                   "### Key Points\n- It helps solve real-world problems\n- It builds on established ideas\n\n### Learn More\n")
        for s in sources_data[:3]:
            summary += f"- [{s.get('title', 'Resource')}]({s.get('url', '#')})\n"
        return summary
