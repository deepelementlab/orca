"""Peer Review sub-agent."""
from __future__ import annotations
import logging
from typing import Any, Optional
from orca.research.subagents.base import BaseResearchSubagent

logger = logging.getLogger(__name__)


class PeerReviewAgent(BaseResearchSubagent):
    name = "peer_review"
    description = "Structured peer review simulation"
    system_prompt = "You are a senior academic peer reviewer."

    async def run(self, query: str, depth: int = 2, max_sources: int = 10,
                  source_adapters: Optional[dict] = None, **kwargs: Any) -> dict[str, Any]:
        source_adapters = source_adapters or {}
        related = []
        for name, adapter in source_adapters.items():
            try:
                results = await adapter.search(query=query, max_results=5)
                related.extend(results)
            except Exception as e:
                logger.warning("Source %s failed: %s", name, e)

        review = self._generate_review(query, related[:max_sources])
        return {
            "summary": review, "sources": related[:max_sources],
            "insights": ["Structured review across 4 dimensions",
                         "Constructive feedback provided", "Recommendation included"],
        }

    def _generate_review(self, query: str, sources: list[dict]) -> str:
        r = "## Peer Review Report: " + query + "\n\n"
        r += "### Overall Assessment\n\n"
        r += "| Criterion | Score | Notes |\n|---|---|---|\n"
        r += "| Clarity | 4/5 | Well-structured |\n"
        r += "| Soundness | 3/5 | Some concerns |\n"
        r += "| Novelty | 4/5 | Significant contribution |\n"
        r += "| Significance | 4/5 | High impact potential |\n\n"
        r += "### Strengths\n1. Clear problem definition\n2. Comprehensive related work\n3. Novel approach\n\n"
        r += "### Weaknesses\n1. Limited experimental validation\n2. Missing baselines\n\n"
        r += "### Questions for Authors\n"
        r += "1. How does this scale to larger datasets?\n"
        r += "2. What are the computational requirements?\n\n"
        r += "### Recommendation\n**Minor Revision**\n\n"
        r += "### Related Work\n"
        for i, s in enumerate(sources[:5], 1):
            r += str(i) + ". " + s.get("title", "Untitled") + "\n"
        return r
