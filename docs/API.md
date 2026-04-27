# Orca API Reference

## Base URL
```
http://localhost:8000
```

## Research Endpoints

### POST /api/research/run
Execute a research workflow asynchronously.

**Request:**
```json
{
  "workflow": "deep_research",
  "query": "Transformer architectures in time series forecasting",
  "depth": 2,
  "max_sources": 10,
  "output_format": "markdown"
}
```

**Response:**
```json
{
  "session_id": "rs_abc123",
  "workflow": "deep_research",
  "status": "running",
  "progress": 0.0,
  "created_at": "2026-04-23T10:00:00"
}
```

### GET /api/research/workflows
List available workflows.

**Response:**
```json
[
  {"name": "deep_research", "description": "Multi-round recursive search", "category": "research"},
  {"name": "lit_review", "description": "Structured literature survey", "category": "academic"}
]
```

### GET /api/research/sessions/{session_id}
Get session status and results.

### GET /api/research/sessions
List all sessions.

### POST /api/research/search
Search across source adapters.

## Skills Endpoints

### GET /api/skills/search?q={query}
Search the skill marketplace.

### POST /api/skills/install
Install a skill by name.

### GET /api/skills/{name}
Get skill details.

## System Endpoints

### GET /health
Health check.

### GET /api/config
Get current configuration.
