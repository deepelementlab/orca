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

    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs) -> ResearchResult:
        summa
