"""Prompt template loader — loads .md workflow templates from the prompts directory."""
from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

_FRONT_MATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


class PromptLoader:
    """Load and cache prompt templates from the prompts/ directory."""

    def __init__(self, prompts_dir: str | Path = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._cache: dict[str, str] = {}

    def load(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]
        path = self.prompts_dir / f"{name}.md"
        content = ""
        if path.exists():
            try:
                raw = path.read_text(encoding="utf-8")
                content = _FRONT_MATTER_RE.sub("", raw).strip()
            except Exception as e:
                logger.error("Failed to load prompt '%s': %s", name, e)
        self._cache[name] = content
        return content

    def load_raw(self, name: str) -> str:
        path = self.prompts_dir / f"{name}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def list_available(self) -> list[str]:
        if not self.prompts_dir.exists():
            return []
        return sorted(p.stem for p in self.prompts_dir.glob("*.md"))

    def clear_cache(self) -> None:
        self._cache.clear()
