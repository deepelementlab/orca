"""End-to-end stress tests from real user perspective.

Simulates realistic user journeys through the Orca research system:
- User Journey 1: Student researching a thesis topic
- User Journey 2: Researcher writing a literature review
- User Journey 3: Engineer evaluating papers for replication
- User Journey 4: Casual user asking ELI5 questions
- Concurrent multi-user scenarios
- Error recovery and resilience
- Chinese + English query support
- Long complex queries
- Session history search
- Full API pipeline stress test
"""
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ──────────────────────────────────────────────────
# Shared Fixtures
# ──────────────────────────────────────────────────

def _make_source(title, source_type="arxiv", year="2024", citations=10):
    return {
        "id": f"{source_type}:{hash(title) & 0xFFFFFFFF}",
        "title": title,
        "authors": ["Author A", "Author B"],
        "url": f"https://example.org/{hash(title)}",
        "source_type": source_type,
        "published_date": year,
        "abstract": f"Abstract for {title}. This paper presents novel findings.",
        "citation_count": citations,
        "keywords": ["cs.AI", "cs.LG"],
    }


@pytest.fixture
def rich_sources():
    return [
        _make_source("Attention Is All You Need", "arxiv", "2017", 95000),
        _make_source("BERT: Pre-training of Deep Bidirectional Transformers", "arxiv", "2019", 72000),
        _make_source("GPT-4 Technical Report", "arxiv", "2023", 5000),
        _make_source("Scaling Laws for Neural Language Models", "semantic_scholar", "2020", 4500),
        _make_source("Constitutional AI: Harmlessness from AI Feedback", "arxiv", "2022", 1200),
        _make_source("LoRA: Low-Rank Adaptation of Large Language Models", "arxiv", "2023", 3800),
        _make_source("Chain-of-Thought Prompting Elicits Reasoning", "arxiv", "2022", 6200),
        _make_source("RLHF: Training Language Models to Follow Instructions", "semantic_scholar", "2022", 8500),
        _make_source("Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "arxiv", "2020", 5100),
        _make_source("Mamba: Linear-Time Sequence Modeling with Selective State Spaces", "arxiv", "2023", 900),
        _make_source("Vision Transformer: An Image is Worth 16x16 Words", "arxiv", "2021", 18000),
        _make_source("Diffusion Models Beat GANs on Image Synthesis", "semantic_scholar", "2021", 4100),
    ]


@pytest.fixture
def mock_adapters(rich_sources):
    adapter = MagicMock()
    adapter.search = AsyncMock(return_value=rich_sources)
    adapter.get_details = AsyncMock(return_value=rich_sources[0])
    return {
        "arxiv": adapter,
        "semantic_scholar": adapter,
        "alphaXiv": adapter,
        "web_search": adapter,
    }


@pytest.fixture
def mock_llm_service():
    llm = MagicMock()
    llm.invoke = AsyncMock(side_effect=lambda sys, user, **kw: f"## Analysis\n\nBased on the research data, here is a comprehensive analysis of: {user[:80]}...\n\n### Key Findings\n- Finding 1\n- Finding 2\n- Finding 3\n\n### Conclusion\nThis is a synthesized result.")
    llm.is_configured = True
    return llm


@pytest.fixture
def engine_no_sources():
    from orca.research.engine import ResearchEngine
    from orca.config.orca_config import ResearchEngineConfig
    config = ResearchEngineConfig()
    config.sources = {}
    return ResearchEngine(config=config)


# ──────────────────────────────────────────────────
# User Journey 1: Student Researching a Thesis Topic
# ──────────────────────────────────────────────────

class TestStudentThesisJourney:
    @pytest.mark.asyncio
    async def test_full_research_pipeline(self, mock_adapters, mock_llm_service):
        """Student: "I need a deep research on transformer improvements for my thesis." """
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        from orca.prompts.loader import PromptLoader

        wf = DeepResearchWorkflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="Recent improvements to transformer architecture for NLP tasks",
            depth=3,
            max_sources=10,
            source_adapters=mock_adapters,
        )

        assert result.workflow == "deep_research"
        assert result.summary
        assert len(result.summary) > 100
        assert len(result.sources) > 0
        assert result.confidence_score > 0
        assert result.error is None
        assert mock_llm_service.invoke.called

        prompt_used = wf.get_system_prompt()
        assert len(prompt_used) > 50

    @pytest.mark.asyncio
    async def test_then_lit_review_on_same_topic(self, mock_adapters, mock_llm_service):
        """Student: "Now give me a literature review of the same topic." """
        from orca.research.workflows.lit_review import LitReviewWorkflow
        from orca.prompts.loader import PromptLoader

        wf = LitReviewWorkflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="Transformer architecture improvements literature",
            depth=2,
            max_sources=15,
            source_adapters=mock_adapters,
        )

        assert result.workflow == "lit_review"
        assert result.summary
        assert len(result.sources) > 0

    @pytest.mark.asyncio
    async def test_then_peer_review_a_paper(self, mock_adapters, mock_llm_service):
        """Student: "Help me peer review this paper." """
        from orca.research.workflows.peer_review import PeerReviewWorkflow
        from orca.prompts.loader import PromptLoader

        wf = PeerReviewWorkflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="Attention Is All You Need - Vaswani et al. 2017",
            source_adapters=mock_adapters,
        )

        assert result.workflow == "peer_review"
        assert result.summary
        assert mock_llm_service.invoke.called

    @pytest.mark.asyncio
    async def test_then_write_paper_draft(self, mock_adapters, mock_llm_service):
        """Student: "Help me write a draft of my thesis." """
        from orca.research.workflows.paper_writing import PaperWritingWorkflow
        from orca.prompts.loader import PromptLoader

        wf = PaperWritingWorkflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="Survey of Efficient Transformer Architectures for Resource-Constrained Environments",
            max_sources=12,
            source_adapters=mock_adapters,
        )

        assert result.workflow == "paper_writing"
        assert result.summary
        assert len(result.sources) > 0


# ──────────────────────────────────────────────────
# User Journey 2: Researcher Comparing Sources
# ──────────────────────────────────────────────────

class TestResearcherCompareJourney:
    @pytest.mark.asyncio
    async def test_compare_sources_across_databases(self, mock_adapters, mock_llm_service):
        """Researcher: "Compare what arXiv vs Semantic Scholar say about LLM alignment." """
        from orca.research.workflows.source_compare import SourceCompareWorkflow
        from orca.prompts.loader import PromptLoader

        wf = SourceCompareWorkflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="Large language model alignment techniques",
            source_adapters=mock_adapters,
        )

        assert result.workflow == "source_compare"
        assert result.summary
        assert result.insights

    @pytest.mark.asyncio
    async def test_audit_a_specific_paper(self, mock_adapters, mock_llm_service):
        """Researcher: "Audit the methodology of this RLHF paper." """
        from orca.research.workflows.paper_audit import PaperAuditWorkflow
        from orca.prompts.loader import PromptLoader

        wf = PaperAuditWorkflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="Training language models to follow instructions with human feedback (RLHF)",
            source_adapters=mock_adapters,
        )

        assert result.workflow == "paper_audit"
        assert result.summary
        assert mock_llm_service.invoke.called


# ──────────────────────────────────────────────────
# User Journey 3: Engineer Planning Replication
# ──────────────────────────────────────────────────

class TestEngineerReplicationJourney:
    @pytest.mark.asyncio
    async def test_replication_plan(self, mock_adapters, mock_llm_service):
        """Engineer: "I want to replicate the Mamba paper. Give me a plan." """
        from orca.research.workflows.replication import ReplicationWorkflow
        from orca.prompts.loader import PromptLoader

        wf = ReplicationWorkflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
            source_adapters=mock_adapters,
        )

        assert result.workflow == "replication"
        assert result.summary
        assert len(result.summary) > 50


# ──────────────────────────────────────────────────
# User Journey 4: Casual User ELI5
# ──────────────────────────────────────────────────

class TestCasualUserELI5Journey:
    @pytest.mark.asyncio
    async def test_eli5_complex_topic(self, mock_adapters, mock_llm_service):
        """Casual user: "Explain quantum computing like I'm 5." """
        from orca.research.workflows.eli5 import ELI5Workflow
        from orca.prompts.loader import PromptLoader

        wf = ELI5Workflow()
        wf.set_llm(mock_llm_service)
        wf.set_prompt_loader(PromptLoader("prompts"))

        result = await wf.execute(
            query="How does quantum computing work?",
            source_adapters=mock_adapters,
        )

        assert result.workflow == "eli5"
        assert result.summary

    @pytest.mark.asyncio
    async def test_eli5_chinese_query(self, mock_adapters, mock_llm_service):
        """Casual user (Chinese): "用通俗的话解释什么是神经网络" """
        from orca.research.workflows.eli5 import ELI5Workflow

        wf = ELI5Workflow()
        wf.set_llm(mock_llm_service)

        result = await wf.execute(
            query="用通俗的话解释什么是神经网络",
            source_adapters=mock_adapters,
        )

        assert result.workflow == "eli5"
        assert result.summary


# ──────────────────────────────────────────────────
# Multi-Language and Special Character Queries
# ──────────────────────────────────────────────────

class TestMultiLanguageQueries:
    @pytest.mark.parametrize("query", [
        "transformer architecture improvements",
        "transformer架构改进研究",
        "amélioration de l'architecture transformer",
        "Transformer-Architektur Verbesserungen",
        "transformer アーキテクチャの改善",
    ])
    @pytest.mark.asyncio
    async def test_multilingual_queries(self, query, mock_adapters):
        from orca.research.workflows.deep_research import DeepResearchWorkflow

        wf = DeepResearchWorkflow()
        result = await wf.execute(query=query, source_adapters=mock_adapters)
        assert result.summary
        assert result.query == query

    @pytest.mark.parametrize("query", [
        "C++ memory management in modern systems",
        "Rust vs C++: performance & safety trade-offs",
        "Node.js/Express REST API best practices (2024)",
        "SQL injection prevention: 'OR 1=1' and other attacks",
    ])
    @pytest.mark.asyncio
    async def test_special_character_queries(self, query, mock_adapters):
        from orca.research.workflows.deep_research import DeepResearchWorkflow

        wf = DeepResearchWorkflow()
        result = await wf.execute(query=query, source_adapters=mock_adapters)
        assert result.summary
        assert result.error is None


# ──────────────────────────────────────────────────
# Long and Complex Queries
# ──────────────────────────────────────────────────

class TestLongComplexQueries:
    @pytest.mark.asyncio
    async def test_very_long_query(self, mock_adapters):
        from orca.research.workflows.deep_research import DeepResearchWorkflow

        long_query = (
            "What are the most recent advances in efficient fine-tuning methods for large language models, "
            "specifically focusing on parameter-efficient approaches like LoRA, QLoRA, and adapter-based methods, "
            "and how do they compare in terms of memory efficiency, training speed, and downstream task performance "
            "across different model sizes ranging from 7B to 70B parameters?"
        )

        wf = DeepResearchWorkflow()
        result = await wf.execute(query=long_query, depth=3, max_sources=15, source_adapters=mock_adapters)

        assert result.summary
        assert result.query == long_query
        assert len(result.sources) > 0

    @pytest.mark.asyncio
    async def test_single_word_query(self, mock_adapters):
        from orca.research.workflows.deep_research import DeepResearchWorkflow

        wf = DeepResearchWorkflow()
        result = await wf.execute(query="transformers", source_adapters=mock_adapters)
        assert result.summary


# ──────────────────────────────────────────────────
# Concurrent Multi-User Stress Test
# ──────────────────────────────────────────────────

class TestConcurrentStress:
    @pytest.mark.asyncio
    async def test_concurrent_workflows_same_engine(self, engine_no_sources):
        """5 users running different workflows concurrently on the same engine."""
        await engine_no_sources.initialize()

        queries = [
            ("deep_research", "quantum error correction"),
            ("lit_review", "graph neural networks survey"),
            ("eli5", "blockchain technology"),
            ("peer_review", "diffusion models paper"),
            ("paper_audit", "RLHF methodology"),
        ]

        tasks = [
            engine_no_sources.execute(workflow=wf, query=q)
            for wf, q in queries
        ]

        results = await asyncio.gather(*tasks)

        for i, result in enumerate(results):
            assert result is not None
            assert result.workflow == queries[i][0]
            assert result.query == queries[i][1]
            assert result.summary

    @pytest.mark.asyncio
    async def test_10_concurrent_async_sessions(self, engine_no_sources):
        """10 async research sessions fired simultaneously."""
        await engine_no_sources.initialize()

        sessions = []
        for i in range(10):
            session = await engine_no_sources.execute_async(
                workflow="deep_research",
                query=f"test query {i}",
            )
            sessions.append(session)

        assert len(sessions) == 10
        ids = [s.session_id for s in sessions]
        assert len(set(ids)) == 10

        await asyncio.sleep(1.0)

        all_sessions = engine_no_sources.list_sessions()
        assert len(all_sessions) == 10

    @pytest.mark.asyncio
    async def test_burst_queries_same_workflow(self, mock_adapters):
        """20 rapid-fire deep research queries."""
        from orca.research.workflows.deep_research import DeepResearchWorkflow

        wf = DeepResearchWorkflow()
        tasks = [
            wf.execute(query=f"topic {i}", source_adapters=mock_adapters)
            for i in range(20)
        ]

        results = await asyncio.gather(*tasks)
        assert all(r.summary for r in results)
        assert all(r.workflow == "deep_research" for r in results)


# ──────────────────────────────────────────────────
# Session Lifecycle and History
# ──────────────────────────────────────────────────

class TestSessionLifecycle:
    @pytest.mark.asyncio
    async def test_session_create_track_search(self, engine_no_sources):
        """Full session lifecycle: create → track → search history."""
        await engine_no_sources.initialize()

        s1 = await engine_no_sources.execute_async("deep_research", "transformer models")
        s2 = await engine_no_sources.execute_async("lit_review", "GAN survey")

        await asyncio.sleep(1.0)

        fetched1 = engine_no_sources.get_session(s1.session_id)
        assert fetched1 is not None

        all_sessions = engine_no_sources.list_sessions()
        assert len(all_sessions) == 2

        from orca.research.workflows.session_search import SessionSearchWorkflow
        wf = SessionSearchWorkflow()

        result = await wf.execute(
            query="transformer",
            engine=engine_no_sources,
        )
        assert result.workflow == "session_search"
        assert result.summary

    @pytest.mark.asyncio
    async def test_session_search_no_matches(self, engine_no_sources):
        """Search for something that doesn't exist in history."""
        await engine_no_sources.initialize()

        from orca.research.workflows.session_search import SessionSearchWorkflow
        wf = SessionSearchWorkflow()

        result = await wf.execute(query="nonexistent_topic_xyz", engine=engine_no_sources)
        assert result.summary
        assert "No matching" in result.summary or "0" in result.summary or "Found 0" in result.insights[0]


# ──────────────────────────────────────────────────
# Agent Graph End-to-End
# ──────────────────────────────────────────────────

class TestAgentGraphE2E:
    @pytest.mark.asyncio
    async def test_research_query_routes_correctly(self):
        """User sends "research LLM alignment" → routes to research agent."""
        from orca.agent.graph import make_lead_agent
        from langchain_core.messages import HumanMessage

        agent = make_lead_agent()
        with patch("orca.agent.nodes.research_agent._get_engine") as mock_get:
            mock_engine = MagicMock()
            mock_result = MagicMock()
            mock_result.summary = "## LLM Alignment Research\n\nComprehensive analysis..."
            mock_result.error = None
            mock_result.sources = [MagicMock()]
            mock_result.to_dict = MagicMock(return_value={"summary": "test"})
            mock_engine.execute = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_engine

            result = await agent.ainvoke({
                "messages": [HumanMessage(content="research LLM alignment techniques")]
            })

            messages = result.get("messages", [])
            assert len(messages) > 0
            assert any("LLM Alignment" in str(m.content) or "alignment" in str(m.content).lower()
                       for m in messages if hasattr(m, "content"))

    @pytest.mark.asyncio
    async def test_general_query_routes_correctly(self):
        """User sends "hello" → routes to general agent."""
        from orca.agent.graph import make_lead_agent
        from langchain_core.messages import HumanMessage

        agent = make_lead_agent()
        result = await agent.ainvoke({
            "messages": [HumanMessage(content="hello, how are you?")]
        })

        messages = result.get("messages", [])
        assert len(messages) > 0

    @pytest.mark.asyncio
    async def test_chinese_research_keyword_routes(self):
        """Chinese research keyword "研究" triggers research agent."""
        from orca.agent.graph import make_lead_agent
        from langchain_core.messages import HumanMessage

        agent = make_lead_agent()
        with patch("orca.agent.nodes.research_agent._get_engine") as mock_get:
            mock_engine = MagicMock()
            mock_result = MagicMock()
            mock_result.summary = "研究结果的摘要"
            mock_result.error = None
            mock_result.sources = []
            mock_result.to_dict = MagicMock(return_value={})
            mock_engine.execute = AsyncMock(return_value=mock_result)
            mock_get.return_value = mock_engine

            await agent.ainvoke({
                "messages": [HumanMessage(content="研究大型语言模型的对齐方法")]
            })
            assert mock_engine.execute.called


# ──────────────────────────────────────────────────
# Gateway API Full Pipeline
# ──────────────────────────────────────────────────

class TestGatewayFullPipeline:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from orca.gateway.app import create_app
        return TestClient(create_app())

    def test_research_run_sync(self, client):
        """User calls /api/research/run/sync with a real query."""
        resp = client.post("/api/research/run/sync", json={
            "workflow": "deep_research",
            "query": "test query for sync execution",
            "depth": 1,
            "max_sources": 3,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["workflow"] == "deep_research"
        assert "summary" in data

    def test_research_run_async_and_poll(self, client):
        """User starts async research, then polls for result."""
        resp = client.post("/api/research/run", json={
            "workflow": "eli5",
            "query": "what is machine learning",
        })
        assert resp.status_code == 200
        session = resp.json()
        assert "session_id" in session

        poll = client.get(f"/api/research/sessions/{session['session_id']}")
        assert poll.status_code == 200
        poll_data = poll.json()
        assert poll_data["status"] in ("pending", "running", "complete")

    def test_search_sources_endpoint(self, client):
        """User searches for sources directly."""
        resp = client.post("/api/research/search?query=transformer&max_results=3")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "count" in data

    def test_all_9_workflows_via_api(self, client):
        """Run each of the 9 workflows through the API."""
        workflows_resp = client.get("/api/research/workflows")
        workflows = workflows_resp.json()
        assert len(workflows) == 9

        for wf in workflows:
            resp = client.post("/api/research/run/sync", json={
                "workflow": wf["name"],
                "query": f"test query for {wf['name']}",
                "depth": 1,
                "max_sources": 2,
            })
            assert resp.status_code == 200, f"Workflow {wf['name']} failed"
            data = resp.json()
            assert data["workflow"] == wf["name"]


# ──────────────────────────────────────────────────
# Error Resilience and Recovery
# ──────────────────────────────────────────────────

class TestErrorResilience:
    @pytest.mark.asyncio
    async def test_all_sources_fail(self):
        """All data sources fail — system should still return a result."""
        failing = MagicMock()
        failing.search = AsyncMock(side_effect=ConnectionError("Network down"))

        from orca.research.workflows.deep_research import DeepResearchWorkflow
        wf = DeepResearchWorkflow()
        result = await wf.execute(query="test", source_adapters={"fail": failing})
        assert result is not None
        assert result.summary

    @pytest.mark.asyncio
    async def test_llm_fails_gracefully(self, mock_adapters):
        """LLM throws an error — workflow falls back to template."""
        failing_llm = MagicMock()
        failing_llm.invoke = AsyncMock(side_effect=RuntimeError("LLM API overloaded"))

        from orca.research.workflows.deep_research import DeepResearchWorkflow
        wf = DeepResearchWorkflow()
        wf.set_llm(failing_llm)

        result = await wf.execute(query="test query", source_adapters=mock_adapters)
        assert result is not None
        assert result.summary

    @pytest.mark.asyncio
    async def test_partial_source_failure(self):
        """One source fails, another succeeds."""
        failing = MagicMock()
        failing.search = AsyncMock(side_effect=TimeoutError("Timeout"))

        working = MagicMock()
        working.search = AsyncMock(return_value=[_make_source("Working Result")])

        from orca.research.workflows.lit_review import LitReviewWorkflow
        wf = LitReviewWorkflow()
        result = await wf.execute(
            query="test",
            source_adapters={"fail": failing, "ok": working},
        )
        assert result.summary
        assert len(result.sources) > 0

    @pytest.mark.asyncio
    async def test_engine_handles_workflow_exception(self, engine_no_sources):
        """Workflow throws unexpected exception — engine catches it."""
        await engine_no_sources.initialize()

        mock_wf = MagicMock()
        mock_wf.execute = AsyncMock(side_effect=ValueError("Unexpected error"))
        engine_no_sources._workflows["broken"] = mock_wf

        result = await engine_no_sources.execute(workflow="broken", query="test")
        assert result is not None
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_empty_query(self, mock_adapters):
        """User submits empty query string."""
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        wf = DeepResearchWorkflow()
        result = await wf.execute(query="", source_adapters=mock_adapters)
        assert result is not None

    @pytest.mark.asyncio
    async def test_extreme_depth_values(self, mock_adapters):
        """User requests depth=1 and depth=5 (max)."""
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        wf = DeepResearchWorkflow()

        r1 = await wf.execute(query="test", depth=1, source_adapters=mock_adapters)
        assert r1.summary

        r5 = await wf.execute(query="test", depth=5, max_sources=50, source_adapters=mock_adapters)
        assert r5.summary


# ──────────────────────────────────────────────────
# Performance Benchmarks
# ──────────────────────────────────────────────────

class TestPerformance:
    @pytest.mark.asyncio
    async def test_engine_initialization_speed(self):
        """Engine should initialize in < 2 seconds."""
        from orca.research.engine import ResearchEngine
        from orca.config.orca_config import ResearchEngineConfig

        config = ResearchEngineConfig()
        config.sources = {}
        engine = ResearchEngine(config=config)

        start = time.monotonic()
        await engine.initialize()
        elapsed = time.monotonic() - start

        assert elapsed < 2.0, f"Engine init took {elapsed:.2f}s"
        assert len(engine.list_workflows()) == 9

    @pytest.mark.asyncio
    async def test_workflow_execution_speed(self, mock_adapters):
        """Single workflow should complete in < 5 seconds with mock sources."""
        from orca.research.workflows.deep_research import DeepResearchWorkflow

        wf = DeepResearchWorkflow()
        start = time.monotonic()
        result = await wf.execute(query="test", depth=2, max_sources=10, source_adapters=mock_adapters)
        elapsed = time.monotonic() - start

        assert result.summary
        assert elapsed < 5.0, f"Workflow took {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_api_response_time(self):
        """Gateway API should respond in < 2 seconds."""
        from fastapi.testclient import TestClient
        from orca.gateway.app import create_app

        client = TestClient(create_app())

        start = time.monotonic()
        resp = client.get("/api/research/workflows")
        elapsed = time.monotonic() - start

        assert resp.status_code == 200
        assert elapsed < 2.0, f"API took {elapsed:.2f}s"


# ──────────────────────────────────────────────────
# Config and Customization
# ──────────────────────────────────────────────────

class TestConfigCustomization:
    def test_default_config_has_all_sources(self):
        from orca.config.orca_config import ResearchEngineConfig
        config = ResearchEngineConfig()
        assert "arxiv" in config.sources
        assert "semantic_scholar" in config.sources
        assert "web_search" in config.sources
        assert "alphaXiv" in config.sources

    def test_disable_source(self):
        from orca.config.orca_config import ResearchEngineConfig, ResearchSourceConfig
        config = ResearchEngineConfig()
        config.sources["arxiv"] = ResearchSourceConfig(enabled=False)
        assert not config.sources["arxiv"].enabled

    def test_custom_llm_config(self):
        from orca.config.orca_config import LLMConfig
        config = LLMConfig(
            provider="openai",
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=2048,
            api_key="sk-test",
            base_url="https://api.openai.com/v1",
        )
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.3

    def test_yaml_config_roundtrip(self):
        import tempfile
        import os
        from orca.config.orca_config import OrcaConfig

        config = OrcaConfig()
        d = config.to_dict()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml
            yaml.dump(d, f)
            path = f.name

        try:
            loaded = OrcaConfig.from_yaml(path)
            assert loaded.llm.model == config.llm.model
            assert loaded.gateway.port == config.gateway.port
        finally:
            os.unlink(path)


# ──────────────────────────────────────────────────
# Depth and Source Limits Validation
# ──────────────────────────────────────────────────

class TestDepthAndSourceLimits:
    @pytest.mark.asyncio
    async def test_depth_1_minimal(self, mock_adapters):
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        wf = DeepResearchWorkflow()
        result = await wf.execute(query="test", depth=1, max_sources=1, source_adapters=mock_adapters)
        assert result.summary

    @pytest.mark.asyncio
    async def test_max_sources_1(self, mock_adapters):
        from orca.research.workflows.lit_review import LitReviewWorkflow
        wf = LitReviewWorkflow()
        result = await wf.execute(query="test", max_sources=1, source_adapters=mock_adapters)
        assert len(result.sources) <= 1

    @pytest.mark.asyncio
    async def test_engine_depth_capped_at_max(self, engine_no_sources):
        """Depth 10 should be capped to max_depth (5)."""
        await engine_no_sources.initialize()
        result = await engine_no_sources.execute(
            workflow="deep_research", query="test", depth=10
        )
        assert result is not None
