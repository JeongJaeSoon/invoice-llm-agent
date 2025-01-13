"""API 예외 처리"""

from typing import Any, cast

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from structlog import get_logger

from src.api.v1.models import ErrorResponse
from src.core.exceptions import AgentError

logger = get_logger()


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """입력 검증 에러 핸들러"""
    error_response = ErrorResponse(
        error="Invalid request",
        code="VALIDATION_ERROR",
        details={"errors": exc.errors()},
    )
    logger.error("요청 검증 실패", error=f"422: {error_response.model_dump()}")
    return JSONResponse(
        status_code=422,
        content={"result": None, **error_response.model_dump()},
    )


async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    """Agent 에러 핸들러"""
    detail = cast(dict[str, Any], exc.detail)
    error_response = ErrorResponse(
        error=detail["error"],
        code=detail["code"],
        details=detail.get("details"),
    )
    logger.error(
        "요청 처리 실패", error=f"{exc.status_code}: {error_response.model_dump()}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"result": None, **error_response.model_dump()},
    )


async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """일반 에러 핸들러"""
    error_response = ErrorResponse(
        error=str(exc),
        code="INTERNAL_SERVER_ERROR",
        details=None,
    )
    logger.error("요청 처리 실패", error=f"500: {error_response.model_dump()}")
    return JSONResponse(
        status_code=500,
        content={"result": None, **error_response.model_dump()},
    )


def register_exception_handlers(app: Any) -> None:
    """예외 핸들러 등록"""
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(AgentError, agent_error_handler)
    app.add_exception_handler(Exception, general_error_handler)
