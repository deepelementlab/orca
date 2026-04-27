"""Base workflow interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional
from orca.models.research import ResearchResult

class BaseWorkflow(ABC):
    name: str = "base"
    description: str = ""
    category: str = "general"

    @abstractmethod
    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs: Any) -> ResearchResult: ...

    def _err(self, workflow: str, query: str, error: str) -> ResearchResult:
        return ResearchResult(workflow=workflow, query=query, error=error)
