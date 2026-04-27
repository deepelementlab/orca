"""Orca Gateway — FastAPI application."""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from orca.config.orca_config import OrcaConfig
from orca.gateway.routers import research, skills_market

logger = logging.getLogger(__name__)

def create_app(config: OrcaConfig | None = None) -> FastAPI:
    """Create and configure the Orca FastAPI application."""
    config = config or OrcaConfig()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        logger.info("Orca Gateway starting...")
        yield
        logger.info("Orca Gateway shutting down...")

    app = FastAPI(
        title="Orca — 全能研究助手",
        description="Research API powered by DeerFlow × Feynman fusion",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.gateway.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(research.router, prefix="/api/research", tags=["research"])
    app.include_router(skills_market.router, prefix="/api/skills", tags=["skills"])

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "orca-gateway"}

    @app.get("/api/config")
    async def get_config():
        return config.to_dict()

    return app
