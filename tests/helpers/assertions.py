"""테스트 검증 헬퍼"""

from typing import Any


def assert_valid_response_format(response_data: dict[str, Any]) -> None:
    """응답 형식 검증 헬퍼"""
    assert "result" in response_data
    assert isinstance(response_data.get("error"), (type(None), str))


def assert_valid_stream_response(response: Any) -> None:
    """스트리밍 응답 형식 검증 헬퍼"""
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
