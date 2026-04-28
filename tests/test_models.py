"""Tests for Orca data models."""
from datetime import datetime

from orca.models.source import Source
from orca.models.citation import Citation
from orca.models.research import ResearchResult, ResearchSession, WorkflowType, SessionStatus


class TestSource:
    def test_create_source(self):
        s = Source(id="arxiv:1234", title="Test Paper")
        assert s.id == "arxiv:1234"
        assert s.title == "Test Paper"
        assert s.source_type == "web"

    def test_source_to_dict(self):
        s = Source(id="test:1", title="T", authors=["A"])
        d = s.to_dict()
        assert d["id"] == "test:1"
        assert d["authors"] == ["A"]

    def test_source_from_dict(self):
        data = {"id": "test:1", "title": "Test", "authors": ["A"], "published_date": "2024-01-01T00:00:00"}
        s = Source.from_dict(data)
        assert s.id == "test:1"
        assert s.published_date == datetime(2024, 1, 1)


class TestCitation:
    def test_create_citation(self):
        c = Citation(source_id="s1", context="test", relevance_score=0.9)
        assert c.source_id == "s1"
        assert c.relevance_score == 0.9

    def test_citation_roundtrip(self):
        c = Citation(source_id="s1", context="ctx")
        d = c.to_dict()
        c2 = Citation.from_dict(d)
        assert c2.source_id == "s1"


class TestResearchResult:
    def test_create_result(self):
        r = ResearchResult(workflow="deep_research", query="test")
        assert r.workflow == "deep_research"
        assert r.confidence_score == 0.0

    def test_result_with_sources(self):
        s = Source(id="s1", title="Paper 1")
        r = ResearchResult(workflow="lit_review", query="test", sources=[s])
        assert len(r.sources) == 1

    def test_result_to_dict(self):
        r = ResearchResult(workflow="test", query="q")
        d = r.to_dict()
        assert d["workflow"] == "test"
        assert isinstance(d["sources"], list)


class TestResearchSession:
    def test_create_session(self):
        s = ResearchSession(session_id="rs_001", workflow="deep_research")
        assert s.status == SessionStatus.PENDING
        assert s.progress == 0.0

    def test_session_to_dict(self):
        s = ResearchSession(session_id="rs_001", workflow="test")
        d = s.to_dict()
        assert d["status"] == "pending"


class TestWorkflowType:
    def test_all_workflows(self):
        assert len(WorkflowType) == 9
        assert WorkflowType.DEEP_RESEARCH.value == "deep_research"
