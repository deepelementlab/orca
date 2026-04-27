"""arXiv data source adapter."""
from __future__ import annotations
import logging
from typing import Any, Optional
from orca.research.sources.base import BaseSourceAdapter
logger = logging.getLogger(__name__)

class ArxivSourceAdapter(BaseSourceAdapter):
    name = "arxiv"
    description = "arXiv preprint repository"

    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
            results = []
            for paper in client.results(search):
                results.append({
                    "id": f"arxiv:{paper.entry_id}", "title": paper.title,
                    "authors": [a.name for a in paper.authors], "url": paper.entry_id,
                    "source_type": "arxiv",
                    "published_date": paper.published.isoformat() if paper.published else None,
                    "abstract": paper.summary, "pdf_url": paper.pdf_url,
                    "doi": paper.doi, "keywords": paper.categories if hasattr(paper, "categories") else []})
            return results
        except Exception as e:
            logger.error("arXiv search failed: %s", e)
            return []

    async def get_details(self, source_id: str) -> Optional[dict[str, Any]]:
        try:
            import arxiv
            arxiv_id = source_id.replace("arxiv:", "").replace("http://arxiv.org/abs/", "")
            search = arxiv.Search(id_list=[arxiv_id])
            for paper in arxiv.Client().results(search):
                return {"id": f"arxiv:{paper.entry_id}", "title": paper.title,
                        "authors": [a.name for a in paper.authors], "url": paper.entry_id,
                        "source_type": "arxiv",
                        "published_date": paper.published.isoformat() if paper.published else None,
                        "abstract": paper.summary, "pdf_url": paper.pdf_url, "doi": paper.doi}
        except Exception as e:
            logger.error("arXiv detail failed: %s", e)
        return None
