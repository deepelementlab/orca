"""Tests for OrcaConfig."""
import pytest
import tempfile
import os
from pathlib import Path

from orca.config.orca_config import OrcaConfig, ResearchEngineConfig, LLMConfig


class TestOrcaConfig:
    def test_default_config(self):
        config = OrcaConfig()
        assert config.research.default_depth == 2
        assert config.gateway.port == 8000
        assert config.llm.model == "gpt-4o"

    def test_from_yaml(self, tmp_path):
        yaml_content = """
research:
  default_depth: 3
  max_depth: 4
gateway:
  port: 9000
llm:
  model: gpt-4o-mini
  temperature: 0.5
log_level: DEBUG
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        config = OrcaConfig.from_yaml(config_file)
        assert config.research.default_depth == 3
        assert config.gateway.port == 9000
        assert config.llm.model == "gpt-4o-mini"
        assert config.llm.temperature == 0.5
        assert config.log_level == "DEBUG"

    def test_from_missing_yaml(self):
        config = OrcaConfig.from_yaml("/nonexistent/path.yaml")
        assert config.research.default_depth == 2  # defaults

    def test_to_dict(self):
        config = OrcaConfig()
        d = config.to_dict()
        assert "research" in d
        assert "gateway" in d
        assert "llm" in d

    def test_env_var_resolution(self, tmp_path):
        os.environ["TEST_ORCA_KEY"] = "sk-test-123"
        yaml_content = """
llm:
  api_key: $TEST_ORCA_KEY
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        config = OrcaConfig.from_yaml(config_file)
        assert config.llm.api_key == "sk-test-123"
        del os.environ["TEST_ORCA_KEY"]
