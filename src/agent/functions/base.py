"""Agent 함수 기본 클래스"""

import time
from abc import ABC, abstractmethod
from typing import Any

from structlog import get_logger

from src.agent.core.types import FunctionMetadata
from src.core.metrics import FUNCTION_CALLS, FUNCTION_DURATION, FUNCTION_ERRORS

logger = get_logger(__name__)


class AgentFunction(ABC):
    """Agent 함수 기본 클래스"""

    name: str
    description: str
    parameters: dict[str, Any]

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """함수 실행 로직"""
        pass

    async def __call__(self, **kwargs: Any) -> Any:
        """함수 실행 및 메트릭 수집"""
        start_time = time.time()
        FUNCTION_CALLS.labels(function_name=self.name).inc()

        try:
            result = await self.execute(**kwargs)
            duration = time.time() - start_time
            FUNCTION_DURATION.labels(function_name=self.name).observe(duration)
            return result
        except Exception as e:
            logger.error(
                "함수 실행 실패",
                function=self.name,
                error=str(e),
            )
            FUNCTION_ERRORS.labels(
                function_name=self.name,
                error_type=type(e).__name__,
            ).inc()
            raise

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
