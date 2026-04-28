"""Base research subagent using LangGraph."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from orca.models.research import ResearchResult
from orca.research.engine import ResearchEngine

logger = logging.getLogger(__name__)

RESEARCHER_PROMPT = (
    "You are Orca's evidence-gathering research subagent. Your role:\n"
    "- Search exhaustively for relevant papers, datasets, and resources\n"
    "- Prioritize recent and highly-cited sources\n"
    "- Cross-reference multiple databases (arXiv, Semantic Scholar, alphaXiv)\n"
    "- Produce structured evidence packages with provenance tracking\n"
    "- Flag conflicting findings and gaps in the literature\n"
    "Always provide source URLs and citation information."
)

REVIEWER_PROMPT = (
    "You are Orca's AI research reviewer. Your role:\n"
    "- Assess methodology soundness and experimental rigor\n"
    "- Evaluate novelty and significance of contributions\n"
    "- Check statistical validity and reproducibility\n"
    "- Provide constructive feedback following scholarly review standards\n"
    "- Rate each dimension on a scale and summarize overall assessment"
)

WRITER_PROMPT = (
    "You are Orca's academic writing subagent. Your role:\n"
    "- Structure papers following IMRaD format (Introduction, Methods, Results, Discussion)\n"
    "- Write clearly and precisely with proper academic tone\n"
    "- Incorporate citations naturally with proper attribution\n"
    "- Generate abstracts that accurately summarize the work\n"
    "- Ensure logical flow between sections"
)

VERIFIER_PROMPT = (
    "You are Orca's verification agent. Your role:\n"
    "- Fact-check all claims against source material\n"
    "- Verify citation accuracy and completeness\n"
    "- Cross-reference statistics and numerical data\n"
    "- Flag unsubstantiated assertions\n"
    "- Produce a verification report with confidence scores"
)


class BaseSubagent(ABC):
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
    system_prompt = RESEARCHER_PROMPT
    description = "深度研究子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("deep_research", query, **kwargs)


class LitReviewAgent(BaseSubagent):
    name = "lit_review_agent"
    system_prompt = RESEARCHER_PROMPT + "\n\nFocus on organizing and synthesizing academic papers into structured reviews."
    description = "文献综述子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("lit_review", query, **kwargs)


class PeerReviewAgent(BaseSubagent):
    name = "peer_review_agent"
    system_prompt = REVIEWER_PROMPT
    description = "同行评审子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("peer_review", query, **kwargs)


class PaperWritingAgent(BaseSubagent):
    name = "paper_writing_agent"
    system_prompt = WRITER_PROMPT
    description = "论文写作子代理"

    async def run(self, query: str, **kwargs: Any) -> ResearchResult:
        if not self.engine._initialized:
            await self.engine.initialize()
        return await self.engine.execute("paper_writing", query, **kwargs)


def make_research_agent():

    async def research_node(state: dict) -> dict:
        engine = ResearchEngine()
        await engine.initialize()
        messages = state.get("messages", [])
        query = messages[-1].content if messages else ""
        result = await engine.execute("deep_research", query)
        return {"messages": [AIMessage(content=result.summary)]}

    graph = StateGraph(dict)
    graph.add_node("research", research_node)
    graph.set_entry_point("research")
    graph.add_edge("research", END)
    return graph.compile()
