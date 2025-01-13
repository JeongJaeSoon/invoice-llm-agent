from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.system.router import mount_metrics
from src.api.system.router import router as system_router
from src.api.v1.exceptions import register_exception_handlers
from src.api.v1.router import router as v1_router
from src.core.config import settings
from src.core.logging import setup_logging

# 로깅 설정
setup_logging()

# FastAPI 앱 생성
app = FastAPI(
    title="Invoice LLM Agent",
    description="LLM Agent for invoice processing",
    version="0.1.0",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 시스템 라우터 등록
app.include_router(system_router)

# API 라우터 등록
app.include_router(v1_router, prefix=settings.api_prefix)

# Prometheus 메트릭 마운트
mount_metrics(app)

# 예외 핸들러 등록
register_exception_handlers(app)
