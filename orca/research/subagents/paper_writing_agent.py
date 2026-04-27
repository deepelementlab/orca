"""Paper Writing sub-agent."""
from __future__ import annotations
import logging
from typing import Any, Optional
from orca.research.subagents.base import BaseResearchSubagent

logger = logging.getLogger(__name__)


class PaperWritingAgent(BaseResearchSubagent):
    name = "paper_writing"
    description = "Academic paper draft generation"
    system_prompt = "You are an academic paper writing assistant."

    async def run(self, query: str, depth: int = 2, max_sources: int = 10,
                  source_adapters: Optional[dict] = None, **kwargs: Any) -> dict[str, Any]:
        source_adapters = source_adapters or {}
        sources = []
        for name, adapter in source_adapters.items():
            try:
                results = await adapter.search(query=query, max_results=max_sources)
                sources.extend(results)
            except Exception as e:
                logger.warning("Source %s failed: %s", name, e)

        sources = sources[:max_sources]
        draft = self._generate_draft(query, sources, depth)
        return {
            "summary": draft, "sources": sources,
            "insights": ["Draft with " + str(len(sources)) + " references",
                         "IMRAD structure followed", "Bibliography included"],
        }

    def _generate_draft(self, query: str, sources: list[dict], depth: int) -> str:
        d = "# " + query + "\n\n"
        d += "## Abstract\n\nThis paper investigates " + query.lower() + ". "
        d += "Through analysis of " + str(len(sources)) + " related works, we identify key trends "
        d += "and propose directions for future research.\n\n"
        d += "## 1. Introduction\n\nThe study of " + query.lower()
        d += " has gained significant attention in recent years.\n\n"
        d += "## 2. Related Work\n\n"
        for i, s in enumerate(sources[:10], 1):
            authors = s.get("authors", ["Unknown"])
            d += "[" + str(i) + "] " + s.get("title", "Untitled") + " - " + ", ".join(authors[:3]) + "\n"
        d += "\n## 3. Methodology\n\n[To be expanded]\n\n"
        d += "## 4. Results\n\n[To be populated]\n\n"
        d += "## 5. Discussion\n\n[Discussion]\n\n"
        d += "## 6. Conclusion\n\n[Conclusion]\n\n"
        d += "## References\n\n"
        for i, s in enumerate(sources[:15], 1):
            d += "[" + str(i) + "] " + s.get("title", "Untitled") + ". " + s.get("url", "") + "\n"
        return d
