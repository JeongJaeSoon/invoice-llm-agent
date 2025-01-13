from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from src.agent.functions.base import AgentFunction


class LLMService(ABC):
    """LLM 서비스 기본 인터페이스"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        functions: list[AgentFunction] | None = None,
        streaming: bool = False,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        """LLM 응답 생성"""
        pass
