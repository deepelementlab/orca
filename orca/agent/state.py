"""Extended agent state for research capabilities."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from langchain_core.messages import BaseMessage

@dataclass
class ResearchState:
    """Research-specific state fields."""
    intent: str = "general"
    research_workflow: Optional[str] = None
    research_query: Optional[str] = None
    research_depth: int = 2
    research_max_sources: int = 10
    research_result: Optional[dict[str, Any]] = None
    research_session_id: Optional[str] = None

@dataclass
class OrcaAgentState:
    """Full Orca agent state."""
    messages: list[BaseMessage] = field(default_factory=list)
    thread_id: str = ""
    research: ResearchState = field(default_factory=ResearchState)
    metadata: dict[str, Any] = field(default_factory=dict)
