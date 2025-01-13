from fastapi import APIRouter, FastAPI
from prometheus_client import make_asgi_app

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """시스템 상태 확인"""
    return {"status": "ok"}


def mount_metrics(app: FastAPI) -> None:
    """Prometheus 메트릭 마운트"""
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
