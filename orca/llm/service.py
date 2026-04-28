"""LLM Service — unified interface for language model interactions."""
from __future__ import annotations

import logging
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from orca.config.orca_config import LLMConfig

logger = logging.getLogger(__name__)


class LLMService:
    """Unified LLM service wrapping LangChain chat models."""

    def __init__(self, config: LLMConfig | None = None):
        config = config or LLMConfig()
        self._config = config
        self._model: BaseChatModel | None = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        provider = self._config.provider.lower()
        if provider in ("openai", "openai_compatible"):
            self._init_openai()
        else:
            logger.warning("Unknown LLM provider '%s', falling back to OpenAI", provider)
            self._init_openai()

    def _init_openai(self) -> None:
        if not self._config.api_key:
            logger.warning("No API key configured; LLM service disabled")
            self._model = None
            return
        from langchain_openai import ChatOpenAI

        kwargs: dict[str, Any] = {
            "model": self._config.model,
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_tokens,
            "api_key": self._config.api_key,
        }
        if self._config.base_url:
            kwargs["base_url"] = self._config.base_url
        self._model = ChatOpenAI(**kwargs)

    @property
    def model(self) -> BaseChatModel:
        if self._model is None:
            raise RuntimeError("LLM model not initialized")
        return self._model

    @property
    def is_configured(self) -> bool:
        return self._model is not None

    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        *,
        history: list[BaseMessage] | None = None,
    ) -> str:
        if self._model is None:
            return user_message
        messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        if history:
            messages.extend(history)
        messages.append(HumanMessage(content=user_message))
        response = await self._model.ainvoke(messages)
        content = getattr(response, "content", None)
        if content is not None:
            return str(content)
        return str(response)

    async def invoke_messages(self, messages: list[BaseMessage]) -> str:
        if self._model is None:
            return ""
        response = await self._model.ainvoke(messages)
        content = getattr(response, "content", None)
        if content is not None:
            return str(content)
        return str(response)
