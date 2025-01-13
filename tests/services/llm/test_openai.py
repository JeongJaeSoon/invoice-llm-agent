"""OpenAI 서비스 테스트"""

from typing import Any, AsyncGenerator, AsyncIterator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.llm.openai import OpenAIService


def create_mock_client(response: Any) -> MagicMock:
    """Mock OpenAI 클라이언트 생성"""
    mock = MagicMock()
    mock.chat = MagicMock()
    mock.chat.completions = MagicMock()
    mock.chat.completions.create = AsyncMock(return_value=response)
    return mock


@pytest.fixture
def openai_service() -> Generator[OpenAIService, None, None]:
    """OpenAI 서비스 fixture"""
    with patch("src.services.llm.openai.AsyncOpenAI") as mock:
        mock.chat = MagicMock()
        mock.chat.completions = MagicMock()
        service = OpenAIService()
        service.client = mock
        yield service


@pytest.mark.asyncio
async def test_generate_simple_response(openai_service: OpenAIService) -> None:
    """단순 텍스트 생성 테스트"""
    # Mock 응답 설정
    mock_msg = MagicMock(content="테스트 응답", function_call=None)
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=mock_msg)]

    openai_service.client = create_mock_client(mock_response)

    # 테스트 실행
    response = await openai_service.generate("테스트 프롬프트")

    # 검증
    assert isinstance(response, dict)
    assert response["content"] == "테스트 응답"
    assert response["function_call"] is None


@pytest.mark.asyncio
async def test_generate_streaming_response(openai_service: OpenAIService) -> None:
    """스트리밍 응답 테스트"""
    # Mock 스트림 청크 생성
    mock_delta1 = MagicMock(content="청크 1", function_call=None)
    mock_delta2 = MagicMock(content="청크 2", function_call=None)
    chunks = [
        MagicMock(choices=[MagicMock(delta=mock_delta1)]),
        MagicMock(choices=[MagicMock(delta=mock_delta2)]),
    ]

    async def mock_stream() -> AsyncGenerator[MagicMock, None]:
        for chunk in chunks:
            yield chunk

    openai_service.client = create_mock_client(mock_stream())

    # 테스트 실행
    responses = []
    result = await openai_service.generate("테스트 프롬프트", streaming=True)
    assert isinstance(result, AsyncIterator)
    async for response in result:
        responses.append(response)

    # 검증
    assert len(responses) == 2
    assert responses[0]["content"] == "청크 1"
    assert responses[1]["content"] == "청크 2"
