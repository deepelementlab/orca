"""Skill registry — manages skill metadata and discovery."""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

class SkillRegistry:
    """Registry for managing skill metadata."""

    def __init__(self, registry_path: str | Path = "skills/registry.json"):
        self.registry_path = Path(registry_path)
        self._registry: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            try:
                self._registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error("Failed to load registry: %s", e)
                self._registry = {}

    def _save(self) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(self._registry, indent=2, ensure_ascii=False), encoding="utf-8")

    def register(self, name: str, metadata: dict[str, Any]) -> None:
        self._registry[name] = metadata
        self._save()

    def unregister(self, name: str) -> None:
        self._registry.pop(name, None)
        self._save()

    def get(self, name: str) -> Optional[dict[str, Any]]:
        return self._registry.get(name)

    def list_all(self) -> dict[str, dict[str, Any]]:
        return dict(self._registry)

    def search(self, query: str) -> list[tuple[str, dict[str, Any]]]:
        query_lower = query.lower()
        return [(name, meta) for name, meta in self._registry.items()
                if query_lower in name.lower()
                or query_lower in meta.get("description", "").lower()
                or query_lower in meta.get("category", "").lower()]
