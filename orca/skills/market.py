"""Skill market — unified skills marketplace."""
from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

class SkillMarket:
    """Unified skills marketplace for Orca."""

    def __init__(self, skills_dir: str | None = None):
        self.skills_dir = Path(skills_dir or os.environ.get("ORCA_SKILLS_DIR", "skills/public"))
        self._cache: list[dict[str, Any]] | None = None

    def list_skills(self) -> list[dict[str, Any]]:
        """List all available skills."""
        if self._cache is not None:
            return self._cache
        skills = []
        if not self.skills_dir.exists():
            logger.warning("Skills directory not found: %s", self.skills_dir)
            return skills
        for skill_dir in sorted(self.skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            meta = {"name": skill_dir.name, "path": str(skill_dir)}
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")
                lines = content.strip().split("\n")
                if lines:
                    meta["title"] = lines[0].lstrip("# ").strip()
                meta["description"] = content[:200]
            else:
                meta["description"] = f"Skill: {skill_dir.name}"
            meta["installed"] = True
            skills.append(meta)
        self._cache = skills
        return skills

    def search_skills(self, query: str) -> list[dict[str, Any]]:
        """Search skills by name or description."""
        query_lower = query.lower()
        all_skills = self.list_skills()
        return [s for s in all_skills
                if query_lower in s.get("name", "").lower()
                or query_lower in s.get("description", "").lower()
                or query_lower in s.get("title", "").lower()]

    def get_skill(self, name: str) -> Optional[dict[str, Any]]:
        """Get a specific skill by name."""
        for skill in self.list_skills():
            if skill["name"] == name:
                return skill
        return None

    def install_skill(self, name: str) -> bool:
        """Mark a skill as installed (placeholder for remote install)."""
        skill = self.get_skill(name)
        if skill:
            skill["installed"] = True
            return True
        return False

    def uninstall_skill(self, name: str) -> bool:
        """Mark a skill as uninstalled."""
        skill = self.get_skill(name)
        if skill:
            skill["installed"] = False
            return True
        return False

    def get_stats(self) -> dict[str, int]:
        """Get marketplace statistics."""
        skills = self.list_skills()
        return {"total": len(skills), "installed": sum(1 for s in skills if s.get("installed"))}
