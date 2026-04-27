# Orca Setup Guide

## Prerequisites
- Python 3.12+
- Node.js 18+ (for TypeScript CLI and Web UI)
- pip/uv for Python package management

## Quick Start

### 1. Install Python Package
```bash
cd Orca
pip install -e .
```

### 2. Configure
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys
```

### 3. Start Gateway
```bash
# Via Python
python -m orca.gateway.app

# Via CLI
python -m orca.cli.python_cli serve

# Via Makefile
make serve
```

### 4. Start Web UI
```bash
cd web
npm install
npm run dev
```

### 5. Use TypeScript CLI
```bash
cd cli
npm install
npm run build
node dist/index.js research --query "your topic" --workflow deep_research
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| OPENAI_API_KEY | OpenAI API key | — |
| ALPHAXIV_API_KEY | alphaXiv API key | — |
| WEB_SEARCH_API_KEY | Web search API key | — |
| ORCA_CONFIG_PATH | Config file path | config.yaml |

## Docker

```bash
docker build -t orca .
docker run -p 8000:8000 -v ./config.yaml:/app/config.yaml orca
```
