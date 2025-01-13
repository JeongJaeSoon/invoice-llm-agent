from typing import Any, Optional

from pydantic import BaseModel, Field


class FunctionParameter(BaseModel):
    """함수 파라미터 정의"""

    type: str
    description: str
    required: bool = False


class FunctionMetadata(BaseModel):
    """함수 메타데이터"""

    name: str
    description: str
    parameters: dict[str, Any]


class AgentRequest(BaseModel):
    """에이전트 요청 모델"""

    input: str = Field(..., min_length=1, max_length=4096)
    functions: Optional[list[str]] = None
    streaming: bool = False


class AgentResponse(BaseModel):
    """에이전트 응답 모델"""

    result: Any
