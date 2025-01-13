from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """에러 응답 모델"""

    error: str = Field(..., description="에러 메시지")
    code: str = Field(..., description="에러 코드")
    details: dict[str, Any] | None = Field(None, description="추가 상세 정보")
