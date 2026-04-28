"""Skills Market API router."""
from __future__ import annotations
import logging

from fastapi import APIRouter, HTTPException

from orca.skills.market import SkillMarket

logger = logging.getLogger(__name__)
router = APIRouter()

_market: SkillMarket | None = None

def get_market() -> SkillMarket:
    global _market
    if _market is None:
        _market = SkillMarket()
    return _market

@router.get("/search")
async def search_skills(q: str, limit: int = 20):
    """Search skills in the market."""
    market = get_market()
    skills = market.search_skills(q)[:limit]
    return {"query": q, "skills": skills, "count": len(skills)}

@router.get("/")
async def list_skills():
    """List all available skills."""
    market = get_market()
    return {"skills": market.list_skills(), "count": len(market.list_skills())}

@router.get("/{skill_name}")
async def get_skill(skill_name: str):
    """Get details for a specific skill."""
    market = get_market()
    skill = market.get_skill(skill_name)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
    return skill

@router.post("/install")
async def install_skill(skill_name: str):
    """Install a skill from the market."""
    market = get_market()
    result = market.install_skill(skill_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
    return {"status": "installed", "skill": skill_name}

@router.delete("/{skill_name}")
async def uninstall_skill(skill_name: str):
    """Uninstall a skill."""
    market = get_market()
    result = market.uninstall_skill(skill_name)
    return {"status": "uninstalled" if result else "not_found", "skill": skill_name}
