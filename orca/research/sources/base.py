"""Base source adapter interface."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseSourceAdapter(ABC):
    """Abstract base class for research data source adapters."""
    name: str = "base"
    description: str = ""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def get_details(self, source_id: str) -> Optional[dict[str, Any]]: ...
