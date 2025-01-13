from typing import Any, cast

from fastapi import Request, status
from fastapi.responses import JSONResponse
from structlog import get_logger

from src.core.exceptions import AgentError
from src.core.types import ErrorResponse

logger = get_logger(__name__)


async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    """에이전트 관련 에러 핸들러"""
    detail = cast(dict[str, Any], exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=detail["error"],
            code=detail["code"],
            details=detail.get("details"),
        ).model_dump(),
    )


async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """일반 예외 핸들러"""
    logger.error("Unhandled error", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR",
            details={"type": exc.__class__.__name__},
        ).model_dump(),
    )


def register_exception_handlers(app: Any) -> None:
    """예외 핸들러 등록"""
    app.add_exception_handler(AgentError, agent_error_handler)
    app.add_exception_handler(Exception, general_error_handler)
