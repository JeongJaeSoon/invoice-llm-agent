"""Agent API 테스트"""

from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient

from src.agent.functions.base import AgentFunction
from src.main import app
from tests.helpers.assertions import assert_valid_response_format


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


@pytest.fixture(scope="module")
def test_app() -> FastAPI:
    """테스트용 FastAPI 앱 fixture"""
    return app


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """비동기 테스트 클라이언트 fixture"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


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


@pytest.mark.asyncio
async def test_chat_simple_response(
    async_client: AsyncClient,
    mock_llm_service: MagicMock,
) -> None:
    """일반 응답 테스트"""
    mock_llm_service.generate.return_value = {"content": "테스트 응답"}

    response = await async_client.post(
        "/api/v1/agent/chat",
        json={"input": "테스트 메시지"},
    )

    assert response.status_code == 200
    data = response.json()
    assert_valid_response_format(data)
    assert data["result"] == "테스트 응답"


@pytest.mark.asyncio
async def test_chat_with_function_call(
    async_client: AsyncClient,
    mock_llm_service: MagicMock,
    mock_function_registry: MagicMock,
) -> None:
    """Function Calling 테스트"""
    mock_function_call = MagicMock()
    mock_function_call.name = "test_function"
    mock_function_call.arguments = '{"param": "test_value"}'
    mock_llm_service.generate.return_value = {"function_call": mock_function_call}

    response = await async_client.post(
        "/api/v1/agent/chat",
        json={
            "input": "테스트 메시지",
            "functions": ["test_function"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert_valid_response_format(data)
    assert data["result"] == {"param": "test_value"}
