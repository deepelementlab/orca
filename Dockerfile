# Orca — 全能研究助手 (DeerFlow × Feynman Fusion)
# Multi-stage build for production

FROM python:3.12-slim AS base
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY orca/ orca/
COPY prompts/ prompts/
COPY skills/ skills/
COPY config.example.yaml config.example.yaml
COPY langgraph.json langgraph.json

# Expose Gateway port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run Gateway
CMD ["uvicorn", "orca.gateway.app:app", "--host", "0.0.0.0", "--port", "8000"]
