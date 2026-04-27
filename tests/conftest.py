"""Test configuration for Orca."""
import asyncio
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_config():
    from orca.config.orca_config import OrcaConfig
    return OrcaConfig()

@pytest.fixture
def sample_source():
    from orca.models.source import Source
    from datetime import datetime
    return Source(id="test:1", title="Test Paper", authors=["Author A"],
                  url="https://example.com", source_type="arxiv",
                  abstract="Test abstract", citation_count=42)
