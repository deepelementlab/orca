"""Semantic Scholar data source adapter."""
from __future__ import annotations
import logging
from typing import Any, Optional
import httpx
from orca.research.sources.base import BaseSourceAdapter
logger = logging.getLogger(__name__)

class SemanticScholarAdapter(BaseSourceAdapter):
    name = "semantic_scholar"
    description = "Semantic Scholar academic search"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = self.base_url or "https://api.semanticscholar.org/graph/v1"

    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        params = {"query": query, "limit": max_results,
                  "fields": "paperId,title,authors,year,abstract,citationCount,url,externalIds"}
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.base_url}/paper/search", params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            return [{"id": f"ss:{p.get('paperId','')}", "title": p.get("title",""),
                     "authors": [a.get("name","") for a in (p.get("authors") or [])],
                     "url": p.get("url",""), "source_type": "semantic_scholar",
                     "published_date": str(p["year"]) if p.get("year") else None,
                     "abstract": p.get("abstract"), "citation_count": p.get("citationCount",0),
                     "doi": (p.get("externalIds") or {}).get("DOI")} for p in data.get("data",[])]
        except Exception as e:
            logger.error("Semantic Scholar search failed: %s", e)
            return []

    async def get_details(self, source_id: str) -> Optional[dict[str, Any]]:
        ss_id = source_id.replace("ss:", "")
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.base_url}/paper/{ss_id}",
                    params={"fields": "paperId,title,authors,year,abstract,citationCount,url"}, headers=headers)
                resp.raise_for_status()
                p = resp.json()
            return {"id": f"ss:{p.get('paperId','')}", "title": p.get("title",""),
                    "authors": [a.get("name","") for a in (p.get("authors") or [])],
                    "url": p.get("url",""), "source_type": "semantic_scholar",
                    "citation_count": p.get("citationCount",0), "abstract": p.get("abstract")}
        except Exception as e:
            logger.error("Semantic Scholar detail failed: %s", e)
        return None
