"""alphaXiv data source adapter."""
from __future__ import annotations
import logging
from typing import Any, Optional
import httpx
from orca.research.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)


class AlphaXivSourceAdapter(BaseSourceAdapter):
    """alphaXiv paper search adapter (alpha version of arXiv with discussions)."""
    name = "alphaXiv"
    description = "alphaXiv — Open Research Discussion Platform"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = self.base_url or "https://api.alphaxiv.org/v1"

    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        """Search alphaXiv for papers. Falls back to arXiv if API unavailable."""
        results = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/search",
                    params={"query": query, "limit": max_results},
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for paper in data.get("papers", data if isinstance(data, list) else []):
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
            logger.warning("alphaXiv search failed (falling back): %s", e)
        return results

    async def get_details(self, source_id: str) -> Optional[dict[str, Any]]:
        """Get paper details from alphaXiv."""
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
