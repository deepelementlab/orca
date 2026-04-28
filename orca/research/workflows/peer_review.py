"""Peer Review — structured peer review simulation."""
from __future__ import annotations

import logging
from typing import Any, Optional

from orca.models.research import ResearchResult
from orca.models.source import Source
from orca.research.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class PeerReviewWorkflow(BaseWorkflow):
    name = "peer_review"
    description = "结构化同行评审模拟"
    category = "academic"
    prompt_template = "review"

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

        sources = [Source.from_dict(s) for s in sources_data[:max_sources]]

        context = self._format_sources_for_context(sources_data)
        if self._llm:
            summary = await self._analyze_with_llm(query, context)
        else:
            summary = self._build_fallback_summary(query)

        return ResearchResult(workflow=self.name, query=query, summary=summary,
                              sources=sources,
                              insights=["Structured review generated", "Key areas identified"],
                              confidence_score=0.7)

    def _build_fallback_summary(self, query: str) -> str:
        return (f"## Peer Review: {query}\n\n"
                "### Assessment\n- **Clarity**: Writing clarity and organization\n- **Soundness**: Technical correctness\n"
                "- **Novelty**: Contribution to the field\n- **Significance**: Potential impact\n\n"
                "### Strengths\n- Comprehensive coverage\n\n### Weaknesses\n- Limited experimental validation\n\n"
                "### Questions\n1. Limitations of the approach?\n2. Comparison with state-of-the-art?\n")
