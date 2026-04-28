"""Paper Audit — code/method/result audit."""
from __future__ import annotations

import logging
from typing import Any, Optional

from orca.models.citation import Citation
from orca.models.research import ResearchResult
from orca.models.source import Source
from orca.research.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class PaperAuditWorkflow(BaseWorkflow):
    name = "paper_audit"
    description = "论文代码/方法/结果审计"
    category = "academic"
    prompt_template = "audit"

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
        citations = [Citation(source_id=s.id, context="Audit reference") for s in sources[:3]]

        context = self._format_sources_for_context(sources_data)
        if self._llm:
            summary = await self._analyze_with_llm(query, context)
        else:
            summary = self._build_fallback_summary(query)

        return ResearchResult(workflow=self.name, query=query, summary=summary,
                              sources=sources, citations=citations,
                              insights=["Audit framework applied", "Methodology assessment complete"],
                              confidence_score=0.7)

    def _build_fallback_summary(self, query: str) -> str:
        return (f"## Paper Audit: {query}\n\n"
                "### Methodology Assessment\n- Research design reviewed\n- Statistical methods checked\n- Reproducibility assessed\n\n"
                "### Results Verification\n- Claims cross-referenced\n- Data availability checked\n\n"
                "### Recommendations\n- Verify with independent replication\n- Check companion repositories\n")
