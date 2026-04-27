"""Research result and session data models."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from orca.models.citation import Citation
from orca.models.source import Source

class WorkflowType(str, Enum):
    """Available research workflow types."""
    DEEP_RESEARCH = "deep_research"
    LIT_REVIEW = "lit_review"
    PAPER_AUDIT = "paper_audit"
    SOURCE_COMPARE = "source_compare"
    PEER_REVIEW = "peer_review"
    PAPER_WRITING = "paper_writing"
    REPLICATION = "replication"
    ELI5 = "eli5"
    SESSION_SEARCH = "session_search"

class SessionStatus(str, Enum):
    """Research session status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    STALE = "stale"

@dataclass
class ResearchResult:
    """研究工作流输出."""
    workflow: str
    query: str
    timestamp: datetime = field(default_factory=datetime.now)
    summary: str = ""
    sources: list[Source] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    raw_data: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {"workflow": self.workflow, "query": self.query,
                "timestamp": self.timestamp.isoformat(), "summary": self.summary,
                "sources": [s.to_dict() for s in self.sources],
                "citations": [c.to_dict() for c in self.citations],
                "insights": self.insights, "confidence_score": self.confidence_score,
                "raw_data": self.raw_data, "error": self.error}

    @classmethod
    def from_dict(cls, data: dict) -> ResearchResult:
        d = dict(data)
        if isinstance(d.get("timestamp"), str):
            d["timestamp"] = datetime.fromisoformat(d["timestamp"])
        d["sources"] = [Source.from_dict(s) if isinstance(s, dict) else s for s in d.get("sources", [])]
        d["citations"] = [Citation.from_dict(c) if isinstance(c, dict) else c for c in d.get("citations", [])]
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

@dataclass
class ResearchSession:
    """研究会话追踪."""
    session_id: str
    workflow: str
    status: SessionStatus = SessionStatus.PENDING
    progress: float = 0.0
    result: Optional[ResearchResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {"session_id": self.session_id, "workflow": self.workflow,
                "status": self.status.value, "progress": self.progress,
                "result": self.result.to_dict() if self.result else None,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(), "error": self.error}
