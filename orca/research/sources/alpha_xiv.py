"""alphaXiv data source adapter with arXiv fallback."""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from orca.research.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)


class AlphaXivSourceAdapter(BaseSourceAdapter):
    """alphaXiv paper search adapter with arXiv fallback."""
    name = "alphaXiv"
    description = "alphaXiv — Open Research Discussion Platform"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = self.base_url or "https://api.alphaxiv.org/v1"

    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        results = await self._search_alphaXiv(query, max_results)
        if not results:
            logger.info("alphaXiv returned no results, falling back to arXiv")
            results = await self._fallback_arxiv(query, max_results)
        return results

    async def _search_alphaXiv(self, query: str, max_results: int) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/search",
                    params={"query": query, "limit": max_results},
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    papers = data.get("papers", data if isinstance(data, list) else [])
                    for paper in papers:
                        results.append({
                            "id": f"alphaXiv:{paper.get('paper_id', paper.get('id', ''))}",
                            "title": paper.get("title", ""),
                            "authors": paper.get("authors", []),
                            "url": paper.get("url", f"https://alphaxiv.org/abs/{paper.get('paper_id', '')}"),
                            "source_type": "alphaXiv",
                            "published_date": paper.get("published_date"),
                            "abstract": paper.get("abstract"),
                            "pdf_url": paper.get("pdf_url"),
                        })
        except Exception as e:
            logger.warning("alphaXiv search failed: %s", e)
        return results

    async def _fallback_arxiv(self, query: str, max_results: int) -> list[dict[str, Any]]:
        try:
            from orca.research.sources.arxiv import ArxivSourceAdapter
            fallback = ArxivSourceAdapter(timeout=self.timeout)
            return await fallback.search(query=query, max_results=max_results)
        except Exception as e:
            logger.warning("arXiv fallback also failed: %s", e)
            return []

    async def get_details(self, source_id: str) -> Optional[dict[str, Any]]:
        alpha_id = source_id.replace("alphaXiv:", "")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/papers/{alpha_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                )
                if resp.status_code == 200:
                    paper = resp.json()
                    return {
                        "id": f"alphaXiv:{alpha_id}",
                        "title": paper.get("title", ""),
                        "authors": paper.get("authors", []),
                        "url": paper.get("url", ""),
                        "source_type": "alphaXiv",
                        "abstract": paper.get("abstract"),
                    }
        except Exception as e:
            logger.warning("alphaXiv detail failed: %s", e)
        return None
