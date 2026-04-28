"""Session Search — search through past research sessions."""
from __future__ import annotations

import logging
from typing import Any, Optional

from orca.models.research import ResearchResult
from orca.research.workflows.base import BaseWorkflow

logger = logging.getLogger(__name__)


class SessionSearchWorkflow(BaseWorkflow):
    name = "session_search"
    description = "历史研究会话搜索"
    category = "search"
    prompt_template = "log"

    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs) -> ResearchResult:
        engine = kwargs.get("engine")
        sessions = engine.list_sessions() if engine else []

        query_lower = query.lower()
        matched = []
        for session in sessions:
            if session.result and (
                query_lower in session.workflow.lower()
                or query_lower in (session.result.query or "").lower()
                or query_lower in (session.result.summary or "").lower()
            ):
                matched.append(session)

        context_lines = []
        for s in matched:
            q = s.result.query if s.result else "N/A"
            status = s.status.value if hasattr(s.status, "value") else str(s.status)
            context_lines.append(f"- Session {s.session_id}: {s.workflow} / {q} [{status}]")

        context = "\n".join(context_lines) if context_lines else "No matching sessions found."

        if self._llm:
            summary = await self._analyze_with_llm(query, context)
        else:
            summary = f"## Session Search: {query}\n\n{context}"

        return ResearchResult(workflow=self.name, query=query, summary=summary,
                              insights=[f"Found {len(matched)} matching sessions"],
                              confidence_score=0.8)
