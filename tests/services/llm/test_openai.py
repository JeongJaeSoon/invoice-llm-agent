"""OpenAI 서비스 테스트"""

from typing import Any, AsyncGenerator, AsyncIterator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent.functions.base import AgentFunction
from src.services.llm.openai import OpenAIService


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


def create_mock_usage(
    prompt_tokens: int, completion_tokens: int, total_tokens: int
) -> MagicMock:
    """Mock usage 생성"""
    return MagicMock(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )


def create_mock_client(response: Any) -> MagicMock:
    """Mock OpenAI 클라이언트 생성"""
    mock = MagicMock()
    mock.chat = MagicMock()
    mock.chat.completions = MagicMock()
    mock.chat.completions.create = AsyncMock(return_value=response)
    mock.usage = create_mock_usage(10, 5, 15)
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
async def test_generate_simple_response(
    openai_service: OpenAIService,
) -> None:
    """단순 텍스트 생성 테스트"""
    # Mock 응답 설정
    mock_msg = MagicMock(content="테스트 응답", function_call=None)
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=mock_msg)]
    mock_response.usage = create_mock_usage(10, 5, 15)

    openai_service.client = create_mock_client(mock_response)

    # 테스트 실행
    response = await openai_service.generate("테스트 프롬프트")

    # 검증
    assert isinstance(response, dict)
    assert response["content"] == "테스트 응답"
    assert response["function_call"] is None


@pytest.mark.asyncio
async def test_generate_with_function_call(
    openai_service: OpenAIService,
) -> None:
    """Function Calling 테스트"""
    # Mock 함수 생성
    mock_function = MockFunction()

    # Mock 응답 설정
    mock_function_call = MagicMock()
    mock_function_call.name = "test_function"
    mock_function_call.arguments = '{"param": "test_value"}'

    mock_msg = MagicMock(content=None, function_call=mock_function_call)
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=mock_msg)]
    mock_response.usage = create_mock_usage(10, 5, 15)

    openai_service.client = create_mock_client(mock_response)

    # 테스트 실행
    response = await openai_service.generate(
        "테스트 프롬프트",
        functions=[mock_function],
    )

    # 검증
    assert isinstance(response, dict)
    assert response["content"] == ""
    assert response["function_call"].name == "test_function"
    assert response["function_call"].arguments == '{"param": "test_value"}'


@pytest.mark.asyncio
async def test_generate_streaming_response(
    openai_service: OpenAIService,
) -> None:
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
    responses: list[dict[str, Any]] = []
    result = await openai_service.generate("테스트 프롬프트", streaming=True)
    assert isinstance(result, AsyncIterator)
    async for response in result:
        responses.append(response)

    # 검증
    assert len(responses) == 2
    assert responses[0]["content"] == "청크 1"
    assert responses[1]["content"] == "청크 2"
