"""공통 테스트 Fixture"""

import os
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient

from src.agent.functions.base import AgentFunction
from src.main import app


class MockFunction(AgentFunction):
    """테스트용 Mock 함수"""

    name = "test_function"
    description = "테스트 함수입니다."
    parameters = {
        "type": "object",
        "properties": {"param": {"type": "string", "description": "테스트 파라미터"}},
    }

    async def execute(self, **kwargs: Any) -> Any:
        return kwargs


@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """전체 테스트에서 사용할 FastAPI 앱"""
    return app


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """비동기 HTTP 클라이언트"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_function() -> AgentFunction:
    """테스트용 에이전트 함수"""
    return MockFunction()


@pytest.fixture
def mock_llm_service() -> Generator[MagicMock, None, None]:
    """LLM 서비스 Mock fixture"""
    with patch("src.api.v1.routes.agent.OpenAIService") as mock:
        service = MagicMock()
        service.generate = AsyncMock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_function_registry() -> Generator[MagicMock, None, None]:
    """함수 레지스트리 Mock fixture"""
    with patch("src.api.v1.routes.agent.FunctionRegistry") as mock:
        registry = MagicMock()
        registry.get_function = MagicMock(return_value=MockFunction())
        mock.load_functions.return_value = registry
        yield registry


@pytest.fixture(autouse=True)
def setup_test_env():
    # 테스트용 더미 API 키 설정
    os.environ["OPENAI_API_KEY"] = "test_dummy_key"
