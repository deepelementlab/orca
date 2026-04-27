"""Replication — experiment replication steps."""
from __future__ import annotations
import logging
from typing import Any, Optional
from orca.models.source import Source
from orca.models.research import ResearchResult
from orca.research.workflows.base import BaseWorkflow
logger = logging.getLogger(__name__)

class ReplicationWorkflow(BaseWorkflow):
    name = "replication"
    description = "实验复现步骤规划"
    category = "academic"

    async def execute(self, query: str, depth: int = 2, max_sources: int = 10,
                      source_adapters: Optional[dict[str, Any]] = None,
                      output_format: str = "markdown", **kwargs) -> ResearchResult:
        source_adapters = source_adapters or {}
        sources_data = []
        for name, adapter in source_adapters.items():
            try:
                sources_data.extend(await adapter.search(query=query, max_results=5))
            except Exception as e:
                logger.warning("Source %s: %s", name, e)
        sources = [Source.from_dict(s) for s in sources_data[:max_sources]]
        summary = f"## Replication Plan: {query}\n\n### Step 1: Understand\n- Read original paper thoroughly\n- Identify key claims\n\n### Step 2: Gather Resources\n- Check code repositories\n- Identify datasets\n- List compute requirements\n\n### Step 3: Implement\n- Reproduce from scratch or use provided code\n- Document deviations\n\n### Step 4: Validate\n- Compare with original\n- Statistical testing\n\n### Step 5: Report\n- Document findings\n- Note discrepancies\n"
        return ResearchResult(workflow=self.name, query=query, summary=summary,
            sources=sources, insights=["5-step replication plan generated"], confidence_score=0.7)
