"""Agent API 에러 케이스 테스트"""

from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from src.core.exceptions import FunctionNotFoundError, LLMError
from tests.helpers.assertions import assert_valid_response_format


@pytest.mark.asyncio
async def test_invalid_input_empty(async_client: AsyncClient) -> None:
    """빈 입력 처리 테스트"""
    response = await async_client.post(
        "/api/v1/agent/chat",
        json={"input": ""},
    )

    assert response.status_code == 422
    data = response.json()
    assert_valid_response_format(data)
    assert data["error"] is not None


@pytest.mark.asyncio
async def test_invalid_input_too_long(async_client: AsyncClient) -> None:
    """너무 긴 입력 처리 테스트"""
    response = await async_client.post(
        "/api/v1/agent/chat",
        json={"input": "a" * 10000},
    )

    assert response.status_code == 422
    data = response.json()
    assert_valid_response_format(data)
    assert data["error"] is not None


@pytest.mark.asyncio
async def test_nonexistent_function(
    async_client: AsyncClient,
    mock_function_registry: MagicMock,
) -> None:
    """존재하지 않는 함수 호출 테스트"""
    mock_function_registry.get_function.side_effect = FunctionNotFoundError(
        "test_function"
    )

    response = await async_client.post(
        "/api/v1/agent/chat",
        json={
            "input": "테스트 메시지",
            "functions": ["nonexistent_function"],
        },
    )

    assert response.status_code == 404
    data = response.json()
    assert_valid_response_format(data)
    assert data["error"] is not None


@pytest.mark.asyncio
async def test_function_execution_error(
    async_client: AsyncClient,
    mock_llm_service: MagicMock,
    mock_function_registry: MagicMock,
) -> None:
    """함수 실행 에러 테스트"""
    mock_function_call = MagicMock()
    mock_function_call.name = "test_function"
    mock_function_call.arguments = '{"param": "test_value"}'
    mock_llm_service.generate.return_value = {"function_call": mock_function_call}

    mock_function = MagicMock()
    mock_function.execute.side_effect = Exception("함수 실행 실패")
    mock_function_registry.get_function.return_value = mock_function

    response = await async_client.post(
        "/api/v1/agent/chat",
        json={
            "input": "테스트 메시지",
            "functions": ["test_function"],
        },
    )

    assert response.status_code == 500
    data = response.json()
    assert_valid_response_format(data)
    assert data["error"] is not None


@pytest.mark.asyncio
async def test_llm_service_error(
    async_client: AsyncClient,
    mock_llm_service: MagicMock,
) -> None:
    """LLM 서비스 에러 테스트"""
    mock_llm_service.generate.side_effect = LLMError("API 호출 실패")

    response = await async_client.post(
        "/api/v1/agent/chat",
        json={"input": "테스트 메시지"},
    )

    assert response.status_code == 500
    data = response.json()
    assert_valid_response_format(data)
    assert data["error"] is not None
