"""API 미들웨어"""

import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from structlog import get_logger

from src.core.metrics import API_REQUEST_DURATION, API_REQUESTS

logger = get_logger()


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus 메트릭스 수집 미들웨어"""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        if request.url.path != "/metrics" or request.url.path != "/health":
            duration = time.time() - start_time
            API_REQUESTS.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
            ).inc()
            API_REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path,
            ).observe(duration)

        return response


async def metrics_endpoint(request: Request) -> Response:
    """Prometheus 메트릭스 엔드포인트"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


def setup_middleware(app: FastAPI) -> None:
    """미들웨어 설정"""
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics_endpoint)
