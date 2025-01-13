"""테스트용 Mock 데이터 생성 헬퍼"""

from typing import Any, AsyncGenerator
from unittest.mock import MagicMock


def create_mock_llm_response(content: str = "테스트 응답") -> dict[str, Any]:
    """LLM 응답 Mock 데이터 생성"""
    return {"content": content, "function_call": None}


def create_mock_function_call(
    function_name: str = "test_function",
    arguments: dict[str, Any] | None = None,
) -> MagicMock:
    """Function Call Mock 데이터 생성"""
    if arguments is None:
        arguments = {"param": "test_value"}
    mock_function_call = MagicMock()
    mock_function_call.name = function_name
    mock_function_call.arguments = str(arguments)
    return mock_function_call


async def create_mock_stream() -> AsyncGenerator[dict[str, Any], None]:
    """Mock 스트림 생성기"""
    yield {"content": "청크 1"}
    yield {"content": "청크 2"}
    yield {"content": "청크 3"}


async def create_mock_function_stream(
    function_name: str = "test_function",
    arguments: dict[str, Any] | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Mock 함수 스트림 생성기"""
    if arguments is None:
        arguments = {"param": "test_value"}
    yield {"content": "청크 1"}
    mock_function_call = create_mock_function_call(function_name, arguments)
    yield {"function_call": mock_function_call}
    yield {"content": "청크 2"}
