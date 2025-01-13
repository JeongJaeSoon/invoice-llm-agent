from typing import Any

from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class AgentError(HTTPException):
    """Agent 기본 예외"""

    def __init__(
        self,
        message: str,
        code: str = "AGENT_ERROR",
        status_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": message,
                "code": code,
                "details": details,
            },
        )


class FunctionNotFoundError(AgentError):
    """함수를 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, function_name: str):
        super().__init__(
            message=f"Function {function_name} not found",
            code="FUNCTION_NOT_FOUND",
            status_code=HTTP_404_NOT_FOUND,
            details={"function_name": function_name},
        )


class FunctionExecutionError(AgentError):
    """함수 실행 중 발생하는 예외"""

    def __init__(self, function_name: str, error: Exception):
        super().__init__(
            message=f"Failed to execute function {function_name}",
            code="FUNCTION_EXECUTION_ERROR",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "function_name": function_name,
                "error": str(error),
            },
        )


class InvalidFunctionError(AgentError):
    """잘못된 함수 정의에 대한 예외"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="INVALID_FUNCTION",
            status_code=HTTP_400_BAD_REQUEST,
            details=details,
        )


class LLMError(AgentError):
    """LLM 관련 예외"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="LLM_ERROR",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ValidationError(AgentError):
    """입력 검증 실패 예외"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )
