"""Web search fallback source adapter."""
from __future__ import annotations
import logging
import re
from typing import Any, Optional
import httpx
from orca.research.sources.base import BaseSourceAdapter
logger = logging.getLogger(__name__)

class WebSearchAdapter(BaseSourceAdapter):
    name = "web_search"
    description = "Web search fallback (DuckDuckGo)"

    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        results = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get("https://html.duckduckgo.com/html/",
                    params={"q": query}, headers={"User-Agent": "Orca/0.1.0"})
                if resp.status_code == 200:
                    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', resp.text)
                    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</[at]', resp.text)
                    for i, (title, snippet) in enumerate(zip(titles[:max_results], snippets[:max_results])):
                        results.append({"id": f"web:{hash(title)}", "title": re.sub(r'<[^>]+>','',title).strip(),
                                        "source_type": "web", "abstract": re.sub(r'<[^>]+>','',snippet).strip()})
        except Exception as e:
            logger.error("Web search failed: %s", e)
        return results

    async def get_details(self, source_id: str) -> Optional[dict[str, Any]]:
        return None
