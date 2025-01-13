from abc import ABC, abstractmethod
from typing import Any

from src.agent.core.types import FunctionMetadata


class AgentFunction(ABC):
    """Agent 함수 기본 클래스"""

    name: str
    description: str
    parameters: dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """함수 실행 로직"""
        pass

    def to_dict(self) -> dict[str, Any]:
        """OpenAI Function Calling 형식으로 변환"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }

    @property
    def metadata(self) -> FunctionMetadata:
        """함수 메타데이터"""
        return FunctionMetadata(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )
