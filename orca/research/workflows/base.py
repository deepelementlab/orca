"""Base workflow interface with LLM integration."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from orca.models.research import ResearchResult

if TYPE_CHECKING:
    from orca.llm.service import LLMService
    from orca.prompts.loader import PromptLoader

logger = logging.getLogger(__name__)


class BaseWorkflow(ABC):
    name: str = "base"
    description: str = ""
    category: str = "general"
    prompt_template: str = ""

    def __init__(self) -> None:
        self._llm: LLMService | None = None
        self._prompt_loader: PromptLoader | None = None

    def set_llm(self, llm: LLMService) -> None:
        self._llm = llm

    def set_prompt_loader(self, loader: PromptLoader) -> None:
        self._prompt_loader = loader

    @abstractmethod
    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs: Any) -> ResearchResult: ...

    def _err(self, workflow: str, query: str, error: str) -> ResearchResult:
        return ResearchResult(workflow=workflow, query=query, error=error)

    def get_system_prompt(self) -> str:
        if self._prompt_loader and self.prompt_template:
            loaded = self._prompt_loader.load(self.prompt_template)
            if loaded:
                return loaded
        return f"You are a research assistant performing {self.name} analysis. Be thorough, cite sources, and provide structured output."

    async def _analyze_with_llm(self, query: str, context: str) -> str:
        if self._llm is None:
            return context
        try:
            system_prompt = self.get_system_prompt()
            return await self._llm.invoke(system_prompt, f"Query: {query}\n\nResearch Data:\n{context}")
        except Exception as e:
            logger.warning("LLM analysis failed, using fallback: %s", e)
            return context

    async def _collect_sources(self, query: str, depth: int, max_sources: int,
                              source_adapters: dict[str, Any]) -> list[dict[str, Any]]:
        sources_data: list[dict[str, Any]] = []
        for name, adapter in source_adapters.items():
            try:
                sources_data.extend(await adapter.search(query=query, max_results=max_sources))
            except Exception as e:
                logger.warning("Source %s: %s", name, e)
        if depth > 1 and sources_data:
            follow_ups = [f"{query} recent advances", f"{query} survey"][:depth - 1]
            for fuq in follow_ups:
                for name, adapter in list(source_adapters.items())[:2]:
                    try:
                        sources_data.extend(await adapter.search(query=fuq, max_results=max_sources // 2))
                    except Exception:
                        pass
        return sources_data[:max_sources]

    def _format_sources_for_context(self, sources_data: list[dict[str, Any]]) -> str:
        if not sources_data:
            return "No sources found."
        lines: list[str] = []
        for i, s in enumerate(sources_data, 1):
            title = s.get("title", "Untitled")
            authors = s.get("authors", [])
            author_str = ", ".join(authors[:3]) if authors else "Unknown"
            url = s.get("url", "")
            abstract = s.get("abstract", "")
            lines.append(f"[{i}] {title} — {author_str}\n    URL: {url}")
            if abstract:
                lines.append(f"    Abstract: {abstract[:300]}")
        return "\n".join(lines)
