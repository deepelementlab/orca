"""Research API router."""
from __future__ import annotations
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from orca.config.orca_config import OrcaConfig
from orca.research.engine import ResearchEngine

logger = logging.getLogger(__name__)
router = APIRouter()

_engine: ResearchEngine | None = None

async def get_engine() -> ResearchEngine:
    global _engine
    if _engine is None:
        _engine = ResearchEngine()
        await _engine.initialize()
    return _engine

class ResearchRequest(BaseModel):
    workflow: str = Field(..., description="Workflow name")
    query: str = Field(..., description="Research query")
    depth: int = Field(default=2, ge=1, le=5)
    max_sources: int = Field(default=10, ge=1, le=100)
    output_format: str = Field(default="markdown")

class WorkflowResponse(BaseModel):
    name: str
    description: str
    category: str

@router.post("/run", response_model=dict)
async def run_research(req: ResearchRequest):
    """Execute a research workflow asynchronously."""
    engine = await get_engine()
    session = await engine.execute_async(
        workflow=req.workflow, query=req.query, depth=req.depth,
        max_sources=req.max_sources, output_format=req.output_format)
    return session.to_dict()

@router.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows():
    """List all available research workflows."""
    engine = await get_engine()
    return engine.list_workflows()

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get research session status and results."""
    engine = await get_engine()
    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session.to_dict()

@router.get("/sessions")
async def list_sessions():
    """List all research sessions."""
    engine = await get_engine()
    return [s.to_dict() for s in engine.list_sessions()]

@router.post("/search")
async def search_sources(query: str, max_results: int = 10, source_type: Optional[str] = None):
    """Search across research source adapters."""
    engine = await get_engine()
    results = await engine.search_sources(query=query, source_type=source_type, max_results=max_results)
    return {"query": query, "results": results, "count": len(results)}
