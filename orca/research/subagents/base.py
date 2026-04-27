"""Base research subagent using LangGraph."""
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from orca.models.research import ResearchResult
from orca.research.engine import ResearchEngine

logger = logging.getLogger(__name__)


class BaseSubagent(ABC):
    """Base class for research subagents."""
    name: str = "base"
    system_prompt: str = "You are a research assistant."
    description: str = ""

    def __init__(self, engine: Optional[ResearchEngine] = None):
        self.engine = engine or ResearchEngine()

    @abstractmethod
    async def run(self, query: str, **kwargs: Any) -> ResearchResult: ...

    def get_system_message(self) -> SystemMessage:
        return SystemMessage(content=self.system_prompt)


class DeepResearchAgent(BaseSubagent):
    name = "deep_research_agent"
    system_prompt = "You are a deep research specialist. Conduct thorough multi-round research, synthesize findings, and produce comprehensive reports."
    description = "深度研究子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("deep_research", query, **kwargs)


class LitReviewAgent(BaseSubagent):
    name = "lit_review_agent"
    system_prompt = "You are a literature review specialist. Organize and synthesize academic papers into structured reviews."
    description = "文献综述子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("lit_review", query, **kwargs)


class PeerReviewAgent(BaseSubagent):
    name = "peer_review_agent"
    system_prompt = "You are a peer review specialist. Provide structured academic peer reviews following scholarly standards."
    description = "同行评审子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("peer_review", query, **kwargs)


class PaperWritingAgent(BaseSubagent):
    name = "paper_writing_agent"
    system_prompt = "You are an academic paper writing specialist. Generate structured paper drafts with proper academic formatting."
    description = "论文写作子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("paper_writing", query, **kwargs)


# Factory for LangGraph
def make_research_agent():
    """Create a LangGraph research agent graph."""
    from orca.agent.state import OrcaAgentState

    async def research_node(state: dict) -> dict:
        engine = ResearchEngine()
        await engine.initialize()
        messages = state.get("messages", [])
        query = messages[-1].content if messages else ""
        result = await engine.execute("deep_research", query)
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content=result.summary)]}

    graph = StateGraph(dict)
    graph.add_node("research", research_node)
    graph.set_entry_point("research")
    graph.add_edge("research", END)
    return graph.compile()
