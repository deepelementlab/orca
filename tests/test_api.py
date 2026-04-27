"""Tests for Gateway API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from orca.gateway.app import create_app
from orca.config.orca_config import OrcaConfig


@pytest.fixture
def app():
    config = OrcaConfig()
    return create_app(config)


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "orca-gateway"


class TestConfigEndpoint:
    @pytest.mark.asyncio
    async def test_get_config(self, client):
        resp = await client.get("/api/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "research" in data
        assert "gateway" in data
        assert "llm" in data


class TestResearchEndpoints:
    @pytest.mark.asyncio
    async def test_list_workflows(self, client):
        resp = await client.get("/api/research/workflows")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 9

    @pytest.mark.asyncio
    async def test_run_research(self, client):
        resp = await client.post("/api/research/run", json={
            "workflow": "deep_research",
            "query": "test query",
            "depth": 1,
            "max_sources": 5,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert data["workflow"] == "deep_research"

    @pytest.mark.asyncio
    async def test_get_session(self, client):
        # First run a research
        run_resp = await client.post("/api/research/run", json={
            "workflow": "eli5", "query": "test", "depth": 1,
        })
        session_id = run_resp.json()["session_id"]
        # Then get it
        resp = await client.get(f"/api/research/sessions/{session_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_list_sessions(self, client):
        resp = await client.get("/api/research/sessions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestSkillsEndpoints:
    @pytest.mark.asyncio
    async def test_list_skills(self, client):
        resp = await client.get("/api/skills/")
        assert resp.status_code == 200
        data = resp.json()
        assert "skills" in data

    @pytest.mark.asyncio
    async def test_search_skills(self, client):
        resp = await client.get("/api/skills/search?q=research")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
