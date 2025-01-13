from fastapi import APIRouter
from prometheus_client import make_asgi_app

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


# Prometheus 메트릭 마운트를 위한 함수
def mount_metrics(app):
    """Prometheus 메트릭 마운트"""
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
