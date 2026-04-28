"""Tests for LLM service."""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestLLMService:
    def test_create_service(self):
        from orca.llm.service import LLMService
        from orca.config.orca_config import LLMConfig
        config = LLMConfig(api_key="test-key", model="gpt-4o")
        service = LLMService(config)
        assert service.is_configured
        assert service._model is not None

    def test_create_service_no_key(self):
        from orca.llm.service import LLMService
        from orca.config.orca_config import LLMConfig
        config = LLMConfig(api_key="", model="gpt-4o")
        service = LLMService(config)
        assert not service.is_configured

    @pytest.mark.asyncio
    async def test_invoke_returns_string(self):
        from orca.llm.service import LLMService
        from orca.config.orca_config import LLMConfig
        config = LLMConfig(api_key="test-key", model="gpt-4o")
        service = LLMService(config)

        mock_response = MagicMock()
        mock_response.content = "Test response"
        service._model = MagicMock()
        service._model.ainvoke = AsyncMock(return_value=mock_response)

        result = await service.invoke("system prompt", "user message")
        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_invoke_messages(self):
        from orca.llm.service import LLMService
        from orca.config.orca_config import LLMConfig
        from langchain_core.messages import HumanMessage
        config = LLMConfig(api_key="test-key", model="gpt-4o")
        service = LLMService(config)

        mock_response = MagicMock()
        mock_response.content = "Response"
        service._model = MagicMock()
        service._model.ainvoke = AsyncMock(return_value=mock_response)

        result = await service.invoke_messages([HumanMessage(content="test")])
        assert result == "Response"

    @pytest.mark.asyncio
    async def test_invoke_no_model_returns_message(self):
        from orca.llm.service import LLMService
        from orca.config.orca_config import LLMConfig
        config = LLMConfig(api_key="", model="gpt-4o")
        service = LLMService(config)
        result = await service.invoke("sys", "user msg")
        assert result == "user msg"
