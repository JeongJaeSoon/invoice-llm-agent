from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.llm.openai import OpenAIService


@pytest.fixture
def openai_service():
    with patch("src.services.llm.openai.AsyncOpenAI") as mock_client:
        service = OpenAIService()
        service.client = mock_client
        yield service


@pytest.mark.asyncio
async def test_generate_simple_response(openai_service):
    """단순 텍스트 생성 테스트"""
    # Mock 응답 설정
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="테스트 응답", function_call=None))
    ]
    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_response
    )

    # 테스트 실행
    response = await openai_service.generate("테스트 프롬프트")

    # 검증
    assert response["content"] == "테스트 응답"
    assert response["function_call"] is None


@pytest.mark.asyncio
async def test_generate_streaming_response(openai_service):
    """스트리밍 응답 테스트"""
    # Mock 스트림 청크 생성
    chunks = [
        MagicMock(
            choices=[MagicMock(delta=MagicMock(content="청크 1", function_call=None))]
        ),
        MagicMock(
            choices=[MagicMock(delta=MagicMock(content="청크 2", function_call=None))]
        ),
    ]

    async def mock_stream():
        for chunk in chunks:
            yield chunk

    openai_service.client.chat.completions.create = AsyncMock(
        return_value=mock_stream()
    )

    # 테스트 실행
    responses = []
    async for response in await openai_service.generate(
        "테스트 프롬프트", streaming=True
    ):
        responses.append(response)

    # 검증
    assert len(responses) == 2
    assert responses[0]["content"] == "청크 1"
    assert responses[1]["content"] == "청크 2"
