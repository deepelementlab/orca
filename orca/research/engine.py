"""Research Engine — 核心研究执行引擎."""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Optional
from orca.config.orca_config import ResearchEngineConfig
from orca.models.research import ResearchResult, ResearchSession, SessionStatus

logger = logging.getLogger(__name__)

class ResearchEngine:
    """研究引擎主类 — 管理工作流注册、执行和会话追踪."""
    def __init__(self, config: Optional[ResearchEngineConfig] = None):
        self.config = config or ResearchEngineConfig()
        self._workflows: dict[str, Any] = {}
        self._sessions: dict[str, ResearchSession] = {}
        self._source_adapters: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self._init_sources()
        self._register_builtin_workflows()
        self._initialized = True
        logger.info("ResearchEngine initialized: %d workflows, %d sources",
                     len(self._workflows), len(self._source_adapters))

    async def _init_sources(self) -> None:
        from orca.research.sources.arxiv import ArxivSourceAdapter
        from orca.research.sources.semantic_scholar import SemanticScholarAdapter
        from orca.research.sources.alpha_xiv import AlphaXivSourceAdapter
        from orca.research.sources.web_search import WebSearchAdapter
        cls_map = {"arxiv": ArxivSourceAdapter, "semantic_scholar": SemanticScholarAdapter,
                   "web_search": WebSearchAdapter}
        for name, src_cfg in self.config.sources.items():
            if not src_cfg.enabled:
                continue
            cls = cls_map.get(name)
            if cls:
                self._source_adapters[name] = cls(
                    api_key=src_cfg.api_key, base_url=src_cfg.base_url, timeout=src_cfg.timeout)

    def _register_builtin_workflows(self) -> None:
        from orca.research.workflows.deep_research import DeepResearchWorkflow
        from orca.research.workflows.lit_review import LitReviewWorkflow
        from orca.research.workflows.paper_audit import PaperAuditWorkflow
        from orca.research.workflows.source_compare import SourceCompareWorkflow
        from orca.research.workflows.peer_review import PeerReviewWorkflow
        from orca.research.workflows.paper_writing import PaperWritingWorkflow
        from orca.research.workflows.replication import ReplicationWorkflow
        from orca.research.workflows.eli5 import ELI5Workflow
        from orca.research.workflows.session_search import SessionSearchWorkflow
        for cls in [DeepResearchWorkflow, LitReviewWorkflow, PaperAuditWorkflow,
                    SourceCompareWorkflow, PeerReviewWorkflow, PaperWritingWorkflow,
                    ReplicationWorkflow, ELI5Workflow, SessionSearchWorkflow]:
            wf = cls()
            self._workflows[wf.name] = wf

    def register_workflow(self, name: str, workflow: Any) -> None:
        self._workflows[name] = workflow

    def list_workflows(self) -> list[dict[str, str]]:
        return [{"name": w.name, "description": w.description, "category": w.category}
                for w in self._workflows.values()]

    def get_workflow(self, name: str) -> Optional[Any]:
        return self._workflows.get(name)

    async def execute(self, workflow: str, query: str, depth: Optional[int] = None,
                      max_sources: Optional[int] = None, output_format: str = "markdown",
                      **kwargs: Any) -> ResearchResult:
        if not self._initialized:
            await self.initialize()
        wf = self._workflows.get(workflow)
        if not wf:
            return ResearchResult(workflow=workflow, query=query,
                                  error=f"Unknown workflow '{workflow}'. Available: {list(self._workflows.keys())}")
        depth = min(depth or self.config.default_depth, self.config.max_depth)
        max_sources = max_sources or self.config.default_max_sources
        return await wf.execute(query=query, depth=depth, max_sources=max_sources,
                                source_adapters=self._source_adapters,
                                output_format=output_format, **kwargs)

    async def execute_async(self, workflow: str, query: str, depth: Optional[int] = None,
                            max_sources: Optional[int] = None, output_format: str = "markdown",
                            **kwargs: Any) -> ResearchSession:
        session_id = f"rs_{uuid.uuid4().hex[:12]}"
        session = ResearchSession(session_id=session_id, workflow=workflow)
        self._sessions[session_id] = session

        async def _run():
            session.status = SessionStatus.RUNNING
            session.updated_at = datetime.now()
            try:
                session.result = await self.execute(workflow=workflow, query=query, depth=depth,
                    max_sources=max_sources, output_format=output_format, **kwargs)
                session.status = SessionStatus.COMPLETE
                session.progress = 1.0
            except Exception as e:
                logger.exception("Session %s failed", session_id)
                session.status = SessionStatus.FAILED
                session.error = str(e)
            finally:
                session.updated_at = datetime.now()

        asyncio.create_task(_run())
        return session

    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[ResearchSession]:
        return list(self._sessions.values())

    async def search_sources(self, query: str, source_type: Optional[str] = None,
                             max_results: int = 10) -> list[dict]:
        if not self._initialized:
            await self.initialize()
        adapters = ({source_type: self._source_adapters[source_type]}
                    if source_type and source_type in self._source_adapters
                    else self._source_adapters)
        results = []
        for name, adapter in adapters.items():
            try:
                results.extend(await adapter.search(query=query, max_results=max_results))
            except Exception as e:
                logger.warning("Source '%s' failed: %s", name, e)
        results.sort(key=lambda x: x.get("citation_count", 0) or 0, reverse=True)
        return results[:max_results]
