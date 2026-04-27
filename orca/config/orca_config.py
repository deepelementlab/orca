"""Orca configuration system."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
import yaml

@dataclass
class ResearchSourceConfig:
    """Configuration for a research data source."""
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 10
    timeout: int = 30

@dataclass
class ResearchEngineConfig:
    """Research engine configuration."""
    default_depth: int = 2
    max_depth: int = 5
    default_max_sources: int = 10
    cache_ttl: int = 3600
    cache_enabled: bool = True
    async_execution: bool = True
    sources: dict[str, ResearchSourceConfig] = field(default_factory=lambda: {
        "alphaXiv": ResearchSourceConfig(),
        "arxiv": ResearchSourceConfig(),
        "semantic_scholar": ResearchSourceConfig(base_url="https://api.semanticscholar.org/graph/v1"),
        "web_search": ResearchSourceConfig(),
    })

@dataclass
class GatewayConfig:
    """Gateway server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    debug: bool = False

@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: Optional[str] = None
    base_url: Optional[str] = None

@dataclass
class OrcaConfig:
    """Root Orca configuration."""
    research: ResearchEngineConfig = field(default_factory=ResearchEngineConfig)
    gateway: GatewayConfig = field(default_factory=GatewayConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    skills_dir: str = "skills/public"
    prompts_dir: str = "prompts"
    log_level: str = "INFO"

    @classmethod
    def from_yaml(cls, path: str | Path) -> OrcaConfig:
        path = Path(path)
        if not path.exists():
            return cls()
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> OrcaConfig:
        research_data = data.get("research", {})
        gateway_data = data.get("gateway", {})
        llm_data = data.get("llm", {})
        sources_data = research_data.pop("sources", {})
        research = ResearchEngineConfig(
            **{k: v for k, v in research_data.items() if k in ResearchEngineConfig.__dataclass_fields__},
            sources={name: ResearchSourceConfig(**cfg) for name, cfg in sources_data.items()})
        gateway = GatewayConfig(**{k: v for k, v in gateway_data.items() if k in GatewayConfig.__dataclass_fields__})
        llm_raw = {k: v for k, v in llm_data.items() if k in LLMConfig.__dataclass_fields__}
        if "api_key" in llm_raw and isinstance(llm_raw["api_key"], str) and llm_raw["api_key"].startswith("$"):
            llm_raw["api_key"] = os.environ.get(llm_raw["api_key"][1:])
        llm = LLMConfig(**llm_raw)
        return cls(research=research, gateway=gateway, llm=llm,
                   skills_dir=data.get("skills_dir", "skills/public"),
                   prompts_dir=data.get("prompts_dir", "prompts"),
                   log_level=data.get("log_level", "INFO"))

    def to_dict(self) -> dict[str, Any]:
        import dataclasses
        return dataclasses.asdict(self)
