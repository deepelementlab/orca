"""Web search fallback source adapter — DuckDuckGo Lite."""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

import httpx

from orca.research.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)

_TITLE_RE = re.compile(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', re.DOTALL)
_SNIPPET_RE = re.compile(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
_HREF_RE = re.compile(r'href="(https?://[^"]+)"')
_TAG_RE = re.compile(r'<[^>]+>')


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


class WebSearchAdapter(BaseSourceAdapter):
    name = "web_search"
    description = "Web search fallback (DuckDuckGo)"

    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={"User-Agent": "Mozilla/5.0 (compatible; Orca/0.1.0)"},
                )
                if resp.status_code != 200:
                    logger.warning("DuckDuckGo returned status %d", resp.status_code)
                    return results

                titles = _TITLE_RE.findall(resp.text)
                snippets = _SNIPPET_RE.findall(resp.text)
                for i in range(min(len(titles), max_results)):
                    title = _strip_html(titles[i])
                    snippet = _strip_html(snippets[i]) if i < len(snippets) else ""
                    results.append({
                        "id": f"web:{hash(title) & 0xFFFFFFFF}",
                        "title": title,
                        "source_type": "web",
                        "abstract": snippet,
                        "url": "",
                    })
        except httpx.TimeoutException:
            logger.warning("Web search timed out for query: %s", query[:50])
        except Exception as e:
            logger.error("Web search failed: %s", e)
        return results

    async def get_details(self, source_id: str) -> Optional[dict[str, Any]]:
        return None
