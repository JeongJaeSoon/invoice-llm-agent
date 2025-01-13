import logging
from typing import Any, Callable, Mapping, MutableMapping

import structlog

from src.core.config import settings


def setup_logging() -> None:
    """애플리케이션 로깅 설정"""

    # 로그 레벨 설정
    log_level = getattr(logging, settings.log_level.upper())

    # structlog 프로세서 설정
    processors: list[
        Callable[
            [Any, str, MutableMapping[str, Any]],
            Mapping[str, Any] | str | bytes | bytearray | tuple[Any, ...],
        ]
    ] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # 개발 환경일 경우 콘솔 출력을 더 읽기 쉽게 설정
    if settings.environment == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """구조화된 로거 인스턴스 반환"""
    logger = structlog.get_logger(name)
    assert isinstance(logger, structlog.BoundLogger)
    return logger
