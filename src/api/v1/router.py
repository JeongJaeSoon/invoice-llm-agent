from fastapi import APIRouter

from src.api.v1.routes import agent

router = APIRouter()
router.include_router(agent.router, prefix="/agent", tags=["agent"])
