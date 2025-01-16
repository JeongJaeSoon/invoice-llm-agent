from abc import ABC, abstractmethod
from typing import Any, Dict


class AgentFunction(ABC):
    """Agent 함수의 기본 클래스입니다."""

    name: str
    description: str
    parameters: Dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs: Dict[str, Any]) -> Any:
        """함수를 실행합니다."""
        pass

    async def __call__(self, **kwargs: Dict[str, Any]) -> Any:
        """함수를 호출합니다. 메트릭스 수집을 위해 사용됩니다."""
        return await self.execute(**kwargs)
