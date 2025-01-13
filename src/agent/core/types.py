from typing import Any

from pydantic import BaseModel


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
    """Agent 요청"""

    input: str | bytes
    streaming: bool = False
    functions: list[str] | None = None


class AgentResponse(BaseModel):
    """Agent 응답"""

    result: Any
    error: str | None = None
