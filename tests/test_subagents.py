"""Tests for research subagents."""
import pytest
from orca.research.subagents.base import (
    BaseSubagent, DeepResearchAgent, LitReviewAgent,
    PeerReviewAgent, PaperWritingAgent, make_research_agent,
)


class TestSubagentBase:
    def test_deep_research_agent_properties(self):
        agent = DeepResearchAgent()
        assert agent.name == "deep_research_agent"
        assert agent.system_prompt
        assert "deep research" in agent.system_prompt.lower()

    def test_lit_review_agent_properties(self):
        agent = LitReviewAgent()
        assert agent.name == "lit_review_agent"
        assert agent.system_prompt

    def test_peer_review_agent_properties(self):
        agent = PeerReviewAgent()
        assert agent.name == "peer_review_agent"
        assert agent.system_prompt

    def test_paper_writing_agent_properties(self):
        agent = PaperWritingAgent()
        assert agent.name == "paper_writing_agent"
        assert agent.system_prompt

    def test_get_system_message(self):
        agent = DeepResearchAgent()
        msg = agent.get_system_message()
        assert msg.content == agent.system_prompt


class TestSubagentExecution:
    @pytest.mark.asyncio
    async def test_deep_research_agent_runs(self):
        agent = DeepResearchAgent()
        result = await agent.run("transformer architecture")
        assert result.workflow == "deep_research"
        assert result.summary

    @pytest.mark.asyncio
    async def test_lit_review_agent_runs(self):
        agent = LitReviewAgent()
        result = await agent.run("GAN survey")
        assert result.workflow == "lit_review"

    @pytest.mark.asyncio
    async def test_peer_review_agent_runs(self):
        agent = PeerReviewAgent()
        result = await agent.run("sample paper review")
        assert result.workflow == "peer_review"

    @pytest.mark.asyncio
    async def test_paper_writing_agent_runs(self):
        agent = PaperWritingAgent()
        result = await agent.run("quantum computing")
        assert result.workflow == "paper_writing"


class TestResearchAgentGraph:
    def test_make_research_agent(self):
        graph = make_research_agent()
        assert graph is not None
