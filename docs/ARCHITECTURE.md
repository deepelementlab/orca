# Orca Architecture

## Overview
Orca fuses enterprise AI Agent and academic research CLI into an omniscient research assistant. LangGraph is the sole runtime with unified ~40 skill ecosystem.

## Architecture Layers
- User Interface: TypeScript CLI + Python CLI + Web UI (Next.js)
- Gateway API: FastAPI with /api/research/* and /api/skills/*
- Agent Orchestration: LangGraph StateGraph (router -> research/general)
- Research Engine: 9 workflows x 5 data sources x 4 subagents
- Skills Market: ~40 unified skills

## Key Components

### Research Engine (orca/research/)
- engine.py (131 LOC): Core orchestrator with workflow registration, sync/async execution, session tracking
- sources/: arxiv, semantic_scholar, web_search, alpha_xiv adapters with fallback
- workflows/: 9 workflows (deep_research, lit_review, paper_audit, source_compare, peer_review, paper_writing, replication, eli5, session_search)
- subagents/: 4 LangGraph subagents wrapping workflows

### Agent System (orca/agent/)
- graph.py: StateGraph with router -> research_agent / general_agent
- state.py: OrcaAgentState with ResearchState extension
- nodes/: route_to_research, research_agent, research_tool

### Gateway API (orca/gateway/)
- app.py: FastAPI with CORS, lifespan, health check
- routers/research.py: POST /run, GET /workflows, GET /sessions, POST /search
- routers/skills_market.py: GET /, GET /search, POST /install, GET /{name}

### CLI
- Python CLI (orca/cli/python_cli.py): Click-based, direct engine access
- TypeScript CLI (cli/): Commander-based, HTTP to Gateway

### Web UI (web/)
- Next.js 14 with Tailwind CSS, dark theme (together.ai style)
- ResearchPanel.tsx: Workflow selector, query input, async polling, result rendering

## Data Models
- Source: id, title, authors, url, source_type, published_date, abstract, citation_count, pdf_url, doi, keywords
- Citation: source_id, context, relevance_score, quote
- ResearchResult: workflow, query, timestamp, summary, sources, citations, insights, confidence_score
- ResearchSession: session_id, workflow, status, progress, result, created_at, updated_at

## Design Decisions
1. LangGraph-only runtime (Pi Hosting eliminated)
2. Async execution with polling for long-running workflows
3. Multi-source fallback: alphaXiv -> arXiv -> Semantic Scholar -> Web Search
4. Dual CLI: Python (direct) + TypeScript (HTTP)
5. Dark theme UI with Tailwind CSS
6. Dataclass models with to_dict/from_dict serialization

## Statistics
- 47 Python source files (~2000 LOC)
- 7 TypeScript files (~213 LOC)
- 9 test files (612 LOC, ~61 test cases)
- 12 prompt templates
- 39+ skills
- 11 API endpoints
