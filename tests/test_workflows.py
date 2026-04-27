"""Tests for all 9 research workflows."""
import pytest
from orca.research.workflows.deep_research import DeepResearchWorkflow
from orca.research.workflows.lit_review import LitReviewWorkflow
from orca.research.workflows.paper_audit import PaperAuditWorkflow
from orca.research.workflows.source_compare import SourceCompareWorkflow
from orca.research.workflows.peer_review import PeerReviewWorkflow
from orca.research.workflows.paper_writing import PaperWritingWorkflow
from orca.research.workflows.replication import ReplicationWorkflow
from orca.research.workflows.eli5 import ELI5Workflow
from orca.research.workflows.session_search import SessionSearchWorkflow


ALL_WORKFLOWS = [
    DeepResearchWorkflow, LitReviewWorkflow, PaperAuditWorkflow,
    SourceCompareWorkflow, PeerReviewWorkflow, PaperWritingWorkflow,
    ReplicationWorkflow, ELI5Workflow, SessionSearchWorkflow,
]


class TestWorkflowRegistration:
    def test_all_workflows_have_name(self):
        for cls in ALL_WORKFLOWS:
            wf = cls()
            assert wf.name, f"{cls.__name__} missing name"
            assert isinstance(wf.name, str)

    def test_all_workflows_have_description(self):
        for cls in ALL_WORKFLOWS:
            wf = cls()
            assert wf.description, f"{cls.__name__} missing description"

    def test_workflow_names_unique(self):
        names = [cls().name for cls in ALL_WORKFLOWS]
        assert len(names) == len(set(names)), f"Duplicate names: {names}"

    def test_workflow_categories(self):
        expected = {"research", "academic", "analysis", "writing", "education", "search"}
        for cls in ALL_WORKFLOWS:
            wf = cls()
            assert wf.category in expected or wf.category == "general", \
                f"{wf.name} has unexpected category: {wf.category}"


class TestWorkflowExecution:
    @pytest.mark.asyncio
    async def test_deep_research_executes(self):
        wf = DeepResearchWorkflow()
        result = await wf.execute(query="test query")
        assert result.workflow == "deep_research"
        assert result.summary
        assert result.query == "test query"

    @pytest.mark.asyncio
    async def test_lit_review_executes(self):
        wf = LitReviewWorkflow()
        result = await wf.execute(query="transformer models")
        assert result.workflow == "lit_review"
        assert result.summary

    @pytest.mark.asyncio
    async def test_paper_audit_executes(self):
        wf = PaperAuditWorkflow()
        result = await wf.execute(query="attention mechanism paper")
        assert result.workflow == "paper_audit"
        assert "Audit" in result.summary

    @pytest.mark.asyncio
    async def test_source_compare_executes(self):
        wf = SourceCompareWorkflow()
        result = await wf.execute(query="CNN vs RNN")
        assert result.workflow == "source_compare"
        assert "Comparison" in result.summary

    @pytest.mark.asyncio
    async def test_peer_review_executes(self):
        wf = PeerReviewWorkflow()
        result = await wf.execute(query="sample paper")
        assert result.workflow == "peer_review"
        assert "Review" in result.summary

    @pytest.mark.asyncio
    async def test_paper_writing_executes(self):
        wf = PaperWritingWorkflow()
        result = await wf.execute(query="quantum computing survey")
        assert result.workflow == "paper_writing"
        assert "Abstract" in result.summary or "Introduction" in result.summary

    @pytest.mark.asyncio
    async def test_replication_executes(self):
        wf = ReplicationWorkflow()
        result = await wf.execute(query="GAN training")
        assert result.workflow == "replication"
        assert "Replication" in result.summary

    @pytest.mark.asyncio
    async def test_eli5_executes(self):
        wf = ELI5Workflow()
        result = await wf.execute(query="neural networks")
        assert result.workflow == "eli5"
        assert "ELI5" in result.summary

    @pytest.mark.asyncio
    async def test_session_search_executes(self):
        wf = SessionSearchWorkflow()
        result = await wf.execute(query="past research")
        assert result.workflow == "session_search"
        assert result.summary

    @pytest.mark.asyncio
    async def test_workflow_with_depth(self):
        wf = DeepResearchWorkflow()
        result = await wf.execute(query="test", depth=3)
        assert result.query == "test"

    @pytest.mark.asyncio
    async def test_workflow_with_max_sources(self):
        wf = DeepResearchWorkflow()
        result = await wf.execute(query="test", max_sources=5)
        assert result.query == "test"

    @pytest.mark.asyncio
    async def test_error_result_creation(self):
        wf = DeepResearchWorkflow()
        result = wf._make_error_result("test_wf", "test_q", "test error")
        assert result.error == "test error"
        assert result.workflow == "test_wf"
