"""API 모델"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """채팅 요청 모델"""

    input: str = Field(..., min_length=1, max_length=4096)
    functions: Optional[list[str]] = None
    streaming: bool = False


class ChatResponse(BaseModel):
    """채팅 응답 모델"""

    result: Any
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """에러 응답 모델"""

    error: str
    code: str
    details: Optional[dict[str, Any]] = None
