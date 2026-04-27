"""Paper Writing — academic paper draft generation."""
from __future__ import annotations
import logging
from typing import Any, Optional
from orca.models.source import Source
from orca.models.citation import Citation
from orca.models.research import ResearchResult
from orca.research.workflows.base import BaseWorkflow
logger = logging.getLogger(__name__)

class PaperWritingWorkflow(BaseWorkflow):
    name = "paper_writing"
    description = "学术论文草稿生成"
    category = "writing"

    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs) -> ResearchResult:
        source_adapters = source_adapters or {}
        sources_data = []
        for name, adapter in source_adapters.items():
            try:
                sources_data.extend(await adapter.search(query=query, max_results=max_sources))
            except Exception as e:
                logger.warning("Source %s: %s", name, e)
        sources = [Source.from_dict(s) for s in sources_data[:max_sources]]
        citations = [Citation(source_id=s.id, context="Reference") for s in sources[:10]]
        summary = f"# {query}\n\n## Abstract\n\n[Auto-generated abstract]\n\n## 1. Introduction\n\nThis paper addresses {query}.\n\n## 2. Related Work\n\n"
        for i, s in enumerate(sources_data[:8], 1):
            summary += f"[{i}] {s.get('title','Untitled')} — {', '.join(s.get('authors',[])[:3])}\n"
        summary += "\n## 3. Methodology\n\n[To be expanded]\n\n## 4. Results\n\n[To be expanded]\n\n## 5. Conclusion\n\n[To be expanded]\n\n## References\n\n"
        for i, s in enumerate(sources_data[:15], 1):
            summary += f"[{i}] {s.get('title','Untitled')}. {s.get('url','')}\n"
        return ResearchResult(workflow=self.name, query=query, summary=summary,
            sources=sources, citations=citations,
            insights=["Draft structure generated", f"{len(sources)} references incorporated"],
            confidence_score=0.65)
