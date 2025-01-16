"""Redis 서비스"""

from typing import Any

import redis.asyncio as redis
from structlog import get_logger

from src.core.config import settings
from src.core.metrics import REDIS_CONNECTIONS

logger = get_logger(__name__)


class RedisService:
    """Redis 서비스"""

    def __init__(self) -> None:
        if settings.redis_host is None or settings.redis_port is None:
            raise ValueError("Redis host and port must be set in the configuration.")

        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
        )
        REDIS_CONNECTIONS.inc()

    async def close(self) -> None:
        """Redis 연결 종료"""
        await self.client.close()
        REDIS_CONNECTIONS.dec()

    async def get(self, key: str) -> Any:
        """키에 해당하는 값 조회"""
        try:
            value = await self.client.get(key)
            return value
        except Exception as e:
            logger.error("Redis GET 실패", key=key, error=str(e))
            raise

    async def set(
        self,
        key: str,
        value: Any,
        expire: int | None = None,
    ) -> None:
        """키-값 쌍 저장"""
        try:
            await self.client.set(key, value, ex=expire)
        except Exception as e:
            logger.error("Redis SET 실패", key=key, error=str(e))
            raise

    async def delete(self, key: str) -> None:
        """키-값 쌍 삭제"""
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error("Redis DELETE 실패", key=key, error=str(e))
            raise
