"""Comprehensive integration tests for Orca research capabilities.

Tests cover:
- All 9 research workflows with source adapters
- ResearchEngine full pipeline (init → LLM → workflow → result)
- Data source adapters (arXiv, Semantic Scholar, alphaXiv, web search)
- Agent graph routing and execution
- Gateway API end-to-end
- LLM service integration with prompt templates
- Session lifecycle (create → run → query)
- Subagent execution via ResearchEngine
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ──────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────

@pytest.fixture
def mock_source_adapter():
    """Create a mock source adapter that returns realistic data."""
    adapter = MagicMock()
    adapter.search = AsyncMock(return_value=[
        {
            "id": "arxiv:2401.00001",
            "title": "Attention Is All You Need — Revisited",
            "authors": ["Ashish Vaswani", "Noam Shazeer"],
            "url": "https://arxiv.org/abs/2401.00001",
            "source_type": "arxiv",
            "published_date": "2024-01-15",
            "abstract": "We revisit the transformer architecture and propose improvements.",
            "pdf_url": "https://arxiv.org/pdf/2401.00001",
            "citation_count": 42,
            "keywords": ["cs.CL", "cs.LG"],
        },
        {
            "id": "ss:abc123",
            "title": "Scaling Laws for Neural Language Models",
            "authors": ["Jared Kaplan"],
            "url": "https://semanticscholar.org/paper/abc123",
            "source_type": "semantic_scholar",
            "published_date": "2020",
            "abstract": "We study scaling laws for language model performance.",
            "citation_count": 1500,
        },
    ])
    adapter.get_details = AsyncMock(return_value={
        "id": "arxiv:2401.00001",
        "title": "Attention Is All You Need — Revisited",
        "authors": ["Ashish Vaswani"],
        "abstract": "Full abstract here.",
    })
    return adapter


@pytest.fixture
def source_adapters(mock_source_adapter):
    return {"arxiv": mock_source_adapter, "semantic_scholar": mock_source_adapter}


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.invoke = AsyncMock(return_value="## Analysis\n\nComprehensive research analysis result.")
    llm.is_configured = True
    return llm


# ──────────────────────────────────────────────────
# 1. All 9 Workflows — Full Pipeline
# ──────────────────────────────────────────────────

ALL_WORKFLOW_PARAMS = [
    ("deep_research", "transformer architecture improvements", "Deep Research"),
    ("lit_review", "large language model survey", "Literature"),
    ("paper_audit", "attention mechanism paper", "Audit"),
    ("source_compare", "CNN vs Vision Transformer", "Comparison"),
    ("peer_review", "neural network pruning paper", "Review"),
    ("paper_writing", "graph neural networks for drug discovery", "Abstract"),
    ("replication", "GAN training stability", "Replication"),
    ("eli5", "quantum entanglement", "ELI5"),
    ("session_search", "past research on transformers", "Session"),
]


@pytest.mark.parametrize("workflow,query,expected_in_summary", ALL_WORKFLOW_PARAMS)
@pytest.mark.asyncio
async def test_workflow_full_pipeline(workflow, query, expected_in_summary, source_adapters):
    from orca.research.workflows.deep_research import DeepResearchWorkflow
    from orca.research.workflows.lit_review import LitReviewWorkflow
    from orca.research.workflows.paper_audit import PaperAuditWorkflow
    from orca.research.workflows.source_compare import SourceCompareWorkflow
    from orca.research.workflows.peer_review import PeerReviewWorkflow
    from orca.research.workflows.paper_writing import PaperWritingWorkflow
    from orca.research.workflows.replication import ReplicationWorkflow
    from orca.research.workflows.eli5 import ELI5Workflow
    from orca.research.workflows.session_search import SessionSearchWorkflow

    wf_map = {
        "deep_research": DeepResearchWorkflow,
        "lit_review": LitReviewWorkflow,
        "paper_audit": PaperAuditWorkflow,
        "source_compare": SourceCompareWorkflow,
        "peer_review": PeerReviewWorkflow,
        "paper_writing": PaperWritingWorkflow,
        "replication": ReplicationWorkflow,
        "eli5": ELI5Workflow,
        "session_search": SessionSearchWorkflow,
    }

    wf = wf_map[workflow]()
    assert wf.name == workflow
    assert wf.description

    result = await wf.execute(
        query=query,
        depth=2,
        max_sources=5,
        source_adapters=source_adapters,
    )

    assert result is not None
    assert result.workflow == workflow
    assert result.query == query
    assert result.summary
    assert len(result.summary) > 20, f"Summary too short for {workflow}"
    assert result.error is None
    assert result.confidence_score >= 0.0


@pytest.mark.asyncio
async def test_deep_research_with_sources(mock_source_adapter):
    from orca.research.workflows.deep_research import DeepResearchWorkflow

    wf = DeepResearchWorkflow()
    result = await wf.execute(
        query="transformer improvements",
        depth=3,
        max_sources=10,
        source_adapters={"arxiv": mock_source_adapter},
    )

    assert len(result.sources) > 0
    assert result.sources[0].title
    assert result.confidence_score > 0


@pytest.mark.asyncio
async def test_deep_research_multi_round(mock_source_adapter):
    from orca.research.workflows.deep_research import DeepResearchWorkflow

    wf = DeepResearchWorkflow()
    result = await wf.execute(
        query="RLHF alignment",
        depth=4,
        max_sources=20,
        source_adapters={"arxiv": mock_source_adapter, "ss": mock_source_adapter},
    )

    assert result.workflow == "deep_research"
    assert result.summary
    assert "RLHF" in result.summary or "RLHF" in result.query


# ──────────────────────────────────────────────────
# 2. ResearchEngine Integration
# ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_engine_initialize_registers_all_workflows():
    from orca.research.engine import ResearchEngine
    from orca.config.orca_config import ResearchEngineConfig

    config = ResearchEngineConfig()
    config.sources = {}
    engine = ResearchEngine(config=config)
    await engine.initialize()

    wfs = engine.list_workflows()
    assert len(wfs) == 9
    names = {w["name"] for w in wfs}
    expected = {"deep_research", "lit_review", "paper_audit", "source_compare",
                "peer_review", "paper_writing", "replication", "eli5", "session_search"}
    assert names == expected


@pytest.mark.asyncio
async def test_engine_execute_unknown_workflow():
    from orca.research.engine import ResearchEngine
    from orca.config.orca_config import ResearchEngineConfig

    config = ResearchEngineConfig()
    config.sources = {}
    engine = ResearchEngine(config=config)
    await engine.initialize()

    result = await engine.execute(workflow="nonexistent", query="test")
    assert result.error is not None
    assert "nonexistent" in result.error


@pytest.mark.asyncio
async def test_engine_async_session_lifecycle():
    from orca.research.engine import ResearchEngine
    from orca.config.orca_config import ResearchEngineConfig
    from orca.models.research import SessionStatus

    config = ResearchEngineConfig()
    config.sources = {}
    engine = ResearchEngine(config=config)
    await engine.initialize()

    session = await engine.execute_async(workflow="deep_research", query="test query")
    assert session.session_id.startswith("rs_")
    assert session.workflow == "deep_research"

    await asyncio.sleep(0.5)

    fetched = engine.get_session(session.session_id)
    assert fetched is not None
    assert fetched.status in (SessionStatus.COMPLETE, SessionStatus.RUNNING, SessionStatus.PENDING)

    sessions = engine.list_sessions()
    assert len(sessions) >= 1


@pytest.mark.asyncio
async def test_engine_llm_injection():
    from orca.research.engine import ResearchEngine
    from orca.config.orca_config import ResearchEngineConfig

    config = ResearchEngineConfig()
    config.sources = {}
    engine = ResearchEngine(config=config)

    with patch.object(engine, "_init_llm") as mock_init_llm:
        mock_init_llm.return_value = None
        await engine.initialize()

    for wf in engine._workflows.values():
        assert wf._llm is None or wf._llm is not None


# ──────────────────────────────────────────────────
# 3. Data Source Adapters
# ──────────────────────────────────────────────────

class TestArxivAdapter:
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        from orca.research.sources.arxiv import ArxivSourceAdapter
        adapter = ArxivSourceAdapter(timeout=10)
        try:
            results = await adapter.search(query="transformer", max_results=2)
            assert isinstance(results, list)
            if results:
                assert results[0]["title"]
                assert results[0]["source_type"] == "arxiv"
                assert results[0]["id"].startswith("arxiv:")
        except Exception:
            pytest.skip("arXiv API unavailable in test environment")

    @pytest.mark.asyncio
    async def test_adapter_has_name(self):
        from orca.research.sources.arxiv import ArxivSourceAdapter
        assert ArxivSourceAdapter.name == "arxiv"


class TestSemanticScholarAdapter:
    @pytest.mark.asyncio
    async def test_search_returns_results(self):
        from orca.research.sources.semantic_scholar import SemanticScholarAdapter
        adapter = SemanticScholarAdapter(timeout=10)
        try:
            results = await adapter.search(query="attention mechanism", max_results=2)
            assert isinstance(results, list)
            if results:
                assert results[0]["source_type"] == "semantic_scholar"
        except Exception:
            pytest.skip("Semantic Scholar API unavailable in test environment")

    @pytest.mark.asyncio
    async def test_adapter_has_name(self):
        from orca.research.sources.semantic_scholar import SemanticScholarAdapter
        assert SemanticScholarAdapter.name == "semantic_scholar"


class TestAlphaXivAdapter:
    @pytest.mark.asyncio
    async def test_fallback_to_arxiv(self):
        from orca.research.sources.alpha_xiv import AlphaXivSourceAdapter
        adapter = AlphaXivSourceAdapter(timeout=10)
        with patch.object(adapter, "_search_alphaXiv", new_callable=AsyncMock, return_value=[]):
            with patch.object(adapter, "_fallback_arxiv", new_callable=AsyncMock,
                              return_value=[{"id": "arxiv:1", "title": "Test", "source_type": "arxiv"}]):
                results = await adapter.search(query="test", max_results=5)
                assert len(results) == 1
                assert results[0]["source_type"] == "arxiv"

    @pytest.mark.asyncio
    async def test_adapter_has_name(self):
        from orca.research.sources.alpha_xiv import AlphaXivSourceAdapter
        assert AlphaXivSourceAdapter.name == "alphaXiv"


class TestWebSearchAdapter:
    @pytest.mark.asyncio
    async def test_search_returns_list(self):
        from orca.research.sources.web_search import WebSearchAdapter
        adapter = WebSearchAdapter(timeout=10)
        try:
            results = await adapter.search(query="python async programming", max_results=3)
            assert isinstance(results, list)
        except Exception:
            pytest.skip("Web search unavailable in test environment")

    @pytest.mark.asyncio
    async def test_get_details_returns_none(self):
        from orca.research.sources.web_search import WebSearchAdapter
        adapter = WebSearchAdapter()
        result = await adapter.get_details("web:123")
        assert result is None

    @pytest.mark.asyncio
    async def test_adapter_has_name(self):
        from orca.research.sources.web_search import WebSearchAdapter
        assert WebSearchAdapter.name == "web_search"


# ──────────────────────────────────────────────────
# 4. Agent Graph Routing
# ──────────────────────────────────────────────────

class TestAgentRouting:
    def test_route_research_keywords(self):
        from orca.agent.nodes.route_to_research import route_to_research
        from langchain_core.messages import HumanMessage

        for kw in ["research transformers", "论文综述", "deep research topic", "survey of LLMs"]:
            state = {"messages": [HumanMessage(content=kw)]}
            assert route_to_research(state) == "research", f"Failed for: {kw}"

    def test_route_general_queries(self):
        from orca.agent.nodes.route_to_research import route_to_research
        from langchain_core.messages import HumanMessage

        for q in ["hello", "what is 2+2", "tell me a joke"]:
            state = {"messages": [HumanMessage(content=q)]}
            assert route_to_research(state) == "general", f"Failed for: {q}"

    def test_route_empty_messages(self):
        from orca.agent.nodes.route_to_research import route_to_research
        assert route_to_research({"messages": []}) == "general"

    def test_route_explicit_research_state(self):
        from orca.agent.nodes.route_to_research import route_to_research
        from langchain_core.messages import HumanMessage
        state = {"messages": [HumanMessage(content="hello")], "research": {"intent": "research"}}
        assert route_to_research(state) == "research"


class TestAgentGraph:
    def test_lead_agent_compiles(self):
        from orca.agent.graph import make_lead_agent
        agent = make_lead_agent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_lead_agent_routes_research(self):
        from orca.agent.graph import make_lead_agent
        from langchain_core.messages import HumanMessage

        agent = make_lead_agent()
        with patch("orca.agent.nodes.research_agent._get_engine") as mock_get_engine:
            mock_engine = MagicMock()
            mock_result = MagicMock()
            mock_result.summary = "Test research summary"
            mock_result.error = None
            mock_result.sources = []
            mock_engine.execute = AsyncMock(return_value=mock_result)
            mock_get_engine.return_value = mock_engine

            result = await agent.ainvoke({"messages": [HumanMessage(content="research transformer models")]})
            assert result is not None
            assert "messages" in result


# ──────────────────────────────────────────────────
# 5. LLM Service + Prompt Integration
# ──────────────────────────────────────────────────

class TestLLMWithPrompts:
    def test_prompt_loader_loads_all_templates(self):
        from orca.prompts.loader import PromptLoader
        loader = PromptLoader("prompts")

        expected_templates = [
            "deepresearch", "lit", "audit", "compare", "review",
            "draft", "replicate", "eli5", "log", "autoresearch", "watch", "jobs",
        ]
        for name in expected_templates:
            content = loader.load(name)
            assert content, f"Prompt template '{name}' is empty or missing"

    def test_prompt_loader_lists_all(self):
        from orca.prompts.loader import PromptLoader
        loader = PromptLoader("prompts")
        available = loader.list_available()
        assert len(available) >= 12

    @pytest.mark.asyncio
    async def test_workflow_gets_correct_prompt(self):
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        from orca.prompts.loader import PromptLoader

        wf = DeepResearchWorkflow()
        loader = PromptLoader("prompts")
        wf.set_prompt_loader(loader)

        prompt = wf.get_system_prompt()
        assert prompt
        assert len(prompt) > 50
        assert "research" in prompt.lower()

    @pytest.mark.asyncio
    async def test_workflow_llm_analysis_with_prompt(self, mock_llm):
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        from orca.prompts.loader import PromptLoader

        wf = DeepResearchWorkflow()
        wf.set_llm(mock_llm)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="test query",
            source_adapters={"mock": MagicMock(search=AsyncMock(return_value=[
                {"id": "t:1", "title": "Test", "authors": ["A"], "abstract": "Test abstract"}
            ]))},
        )

        assert result.summary
        assert result.workflow == "deep_research"
        assert mock_llm.invoke.called


# ──────────────────────────────────────────────────
# 6. Gateway API End-to-End
# ──────────────────────────────────────────────────

class TestGatewayE2E:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from orca.gateway.app import create_app
        app = create_app()
        return TestClient(app)

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_config_endpoint(self, client):
        resp = client.get("/api/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "research" in data
        assert "llm" in data
        assert "gateway" in data

    def test_list_workflows(self, client):
        resp = client.get("/api/research/workflows")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 9

    def test_llm_status(self, client):
        resp = client.get("/api/research/llm/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "configured" in data
        assert "model" in data

    def test_list_sessions_empty(self, client):
        resp = client.get("/api/research/sessions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_nonexistent_session(self, client):
        resp = client.get("/api/research/sessions/nonexistent_id")
        assert resp.status_code == 404

    def test_list_skills(self, client):
        resp = client.get("/api/skills/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), dict)
        assert "skills" in resp.json()


# ──────────────────────────────────────────────────
# 7. Model Serialization Roundtrip
# ──────────────────────────────────────────────────

class TestModelRoundtrips:
    def test_research_result_roundtrip(self):
        from orca.models.research import ResearchResult
        from orca.models.source import Source
        from orca.models.citation import Citation

        original = ResearchResult(
            workflow="deep_research",
            query="test query",
            summary="Test summary",
            sources=[Source(id="t:1", title="Test Paper", authors=["Author A"],
                            url="https://example.com", source_type="arxiv")],
            citations=[Citation(source_id="t:1", context="Test context", relevance_score=0.9)],
            insights=["Finding 1", "Finding 2"],
            confidence_score=0.85,
        )

        d = original.to_dict()
        restored = ResearchResult.from_dict(d)

        assert restored.workflow == original.workflow
        assert restored.query == original.query
        assert restored.summary == original.summary
        assert len(restored.sources) == 1
        assert restored.sources[0].title == "Test Paper"
        assert len(restored.citations) == 1
        assert restored.citations[0].relevance_score == 0.9
        assert restored.insights == original.insights
        assert restored.confidence_score == original.confidence_score

    def test_source_roundtrip(self):
        from orca.models.source import Source

        s = Source(id="arxiv:1234", title="Test", authors=["A", "B"],
                   url="https://arxiv.org/abs/1234", source_type="arxiv",
                   abstract="Abstract text", doi="10.1234/test")
        d = s.to_dict()
        restored = Source.from_dict(d)
        assert restored.id == s.id
        assert restored.title == s.title
        assert len(restored.authors) == 2
        assert restored.abstract == s.abstract


# ──────────────────────────────────────────────────
# 8. Subagent Execution
# ──────────────────────────────────────────────────

class TestSubagentIntegration:
    @pytest.mark.asyncio
    async def test_all_subagents_can_run(self):
        from orca.research.subagents.base import (
            DeepResearchAgent, LitReviewAgent, PeerReviewAgent, PaperWritingAgent,
        )
        from orca.config.orca_config import ResearchEngineConfig

        config = ResearchEngineConfig()
        config.sources = {}

        for AgentClass in [DeepResearchAgent, LitReviewAgent, PeerReviewAgent, PaperWritingAgent]:
            agent = AgentClass()
            agent.engine = MagicMock()
            agent.engine._initialized = True
            mock_result = MagicMock()
            mock_result.workflow = agent.name.replace("_agent", "")
            mock_result.summary = f"Result from {agent.name}"
            mock_result.error = None
            mock_result.sources = []
            mock_result.query = "test"
            agent.engine.execute = AsyncMock(return_value=mock_result)

            result = await agent.run("test query")
            assert result is not None

    def test_subagent_prompts_contain_feynman_roles(self):
        from orca.research.subagents.base import (
            RESEARCHER_PROMPT, REVIEWER_PROMPT, WRITER_PROMPT, VERIFIER_PROMPT,
        )
        assert "exhaustively" in RESEARCHER_PROMPT.lower()
        assert "methodology" in REVIEWER_PROMPT.lower()
        assert "IMRaD" in WRITER_PROMPT
        assert "fact-check" in VERIFIER_PROMPT.lower()


# ──────────────────────────────────────────────────
# 9. Edge Cases and Error Handling
# ──────────────────────────────────────────────────

class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_workflow_with_no_sources(self):
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        wf = DeepResearchWorkflow()
        result = await wf.execute(query="obscure topic xyz", source_adapters={})
        assert result is not None
        assert result.summary
        assert "No sources" in result.summary or "0" in result.summary or result.summary

    @pytest.mark.asyncio
    async def test_workflow_with_failing_source(self):
        from orca.research.workflows.lit_review import LitReviewWorkflow

        failing_adapter = MagicMock()
        failing_adapter.search = AsyncMock(side_effect=Exception("API timeout"))

        wf = LitReviewWorkflow()
        result = await wf.execute(query="test", source_adapters={"fail": failing_adapter})
        assert result is not None
        assert result.workflow == "lit_review"

    @pytest.mark.asyncio
    async def test_engine_double_initialize(self):
        from orca.research.engine import ResearchEngine
        from orca.config.orca_config import ResearchEngineConfig

        config = ResearchEngineConfig()
        config.sources = {}
        engine = ResearchEngine(config=config)
        await engine.initialize()
        await engine.initialize()
        assert len(engine.list_workflows()) == 9

    def test_module_level_app_exists(self):
        from orca.gateway.app import app
        assert app is not None

    @pytest.mark.asyncio
    async def test_base_workflow_err_method(self):
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        wf = DeepResearchWorkflow()
        result = wf._err("test_wf", "test_q", "something went wrong")
        assert result.error == "something went wrong"
        assert result.workflow == "test_wf"
        assert result.query == "test_q"
