"""Tests for Skills market and registry."""

from orca.skills.market import SkillMarket
from orca.skills.registry import SkillRegistry


class TestSkillMarket:
    def test_list_skills(self):
        market = SkillMarket(skills_dir="skills/public")
        skills = market.list_skills()
        assert isinstance(skills, list)

    def test_search_skills(self):
        market = SkillMarket(skills_dir="skills/public")
        results = market.search_skills("research")
        assert isinstance(results, list)

    def test_get_skill(self):
        market = SkillMarket(skills_dir="skills/public")
        skills = market.list_skills()
        if skills:
            skill = market.get_skill(skills[0]["name"])
            assert skill is not None

    def test_get_stats(self):
        market = SkillMarket(skills_dir="skills/public")
        stats = market.get_stats()
        assert "total" in stats
        assert "installed" in stats


class TestSkillRegistry:
    def test_register_and_get(self, tmp_path):
        registry = SkillRegistry(registry_path=tmp_path / "reg.json")
        registry.register("test-skill", {"description": "A test skill", "category": "test"})
        skill = registry.get("test-skill")
        assert skill is not None
        assert skill["description"] == "A test skill"

    def test_search(self, tmp_path):
        registry = SkillRegistry(registry_path=tmp_path / "reg.json")
        registry.register("deep-research", {"description": "Deep research", "category": "research"})
        registry.register("eli5", {"description": "Explain like I am 5", "category": "education"})
        results = registry.search("research")
        assert len(results) == 1
        assert results[0][0] == "deep-research"

    def test_unregister(self, tmp_path):
        registry = SkillRegistry(registry_path=tmp_path / "reg.json")
        registry.register("temp-skill", {"description": "Temporary"})
        registry.unregister("temp-skill")
        assert registry.get("temp-skill") is None
