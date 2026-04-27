"""Tests for ResearchEngine."""
import pytest
from orca.research.engine import ResearchEngine
from orca.config.orca_config import ResearchEngineConfig


@pytest.fixture
def engine():
    return ResearchEngine(config=ResearchEngineConfig())


class TestResearchEngine:
    @pytest.mark.asyncio
    async def test_initialize(self, engine):
        await engine.initialize()
        assert engine._initialized
        assert len(engine._workflows) == 9

    @pytest.mark.asyncio
    async def test_list_workflows(self, engine):
        await engine.initialize()
        workflows = engine.list_workflows()
        assert len(workflows) == 9
        names = [w["name"] for w in workflows]
        assert "deep_research" in names
        assert "lit_review" in names

    @pytest.mark.asyncio
    async def test_unknown_workflow(self, engine):
        await engine.initialize()
        result = await engine.execute("nonexistent", "test query")
        assert result.error is not None
        assert "Unknown workflow" in result.error

    @pytest.mark.asyncio
    async def test_execute_deep_research(self, engine):
        await engine.initialize()
        result = await engine.execute("deep_research", "transformer architecture")
        assert result.workflow == "deep_research"
        assert result.query == "transformer architecture"
        assert result.summary  # Has some output

    @pytest.mark.asyncio
    async def test_execute_async(self, engine):
        await engine.initialize()
        session = await engine.execute_async("deep_research", "test query")
        assert session.session_id.startswith("rs_")
        assert session.workflow == "deep_research"

    @pytest.mark.asyncio
    async def test_get_session(self, engine):
        await engine.initialize()
        session = await engine.execute_async("eli5", "quantum computing")
        retrieved = engine.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    @pytest.mark.asyncio
    async def test_list_sessions(self, engine):
        await engine.initialize()
        await engine.execute_async("eli5", "test1")
        await engine.execute_async("eli5", "test2")
        sessions = engine.list_sessions()
        assert len(sessions) >= 2
