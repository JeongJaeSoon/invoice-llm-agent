"""Agent API 라우터"""

import json
from typing import AsyncIterator, Final

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from structlog import get_logger

from src.agent.core.types import AgentRequest, AgentResponse
from src.agent.functions.registry import FunctionRegistry
from src.core.exceptions import (
    FunctionExecutionError,
    FunctionNotFoundError,
    LLMError,
    ValidationError,
)
from src.services.llm.openai import OpenAIService

router = APIRouter()
logger = get_logger(__name__)


def get_llm_service() -> OpenAIService:
    return OpenAIService()


def get_function_registry() -> FunctionRegistry:
    return FunctionRegistry.load_functions()


# 의존성 상수 정의
LLM_SERVICE_DEPENDS: Final = Depends(get_llm_service)
FUNCTION_REGISTRY_DEPENDS: Final = Depends(get_function_registry)


@router.post("/chat")
async def chat(
    request: AgentRequest,
    llm_service: OpenAIService = LLM_SERVICE_DEPENDS,
    registry: FunctionRegistry = FUNCTION_REGISTRY_DEPENDS,
) -> AgentResponse:
    """LLM과 대화"""
    try:
        # 요청된 함수들 가져오기
        functions = None
        if request.functions:
            try:
                functions = [registry.get_function(name) for name in request.functions]
            except FunctionNotFoundError as e:
                logger.error("함수를 찾을 수 없음", error=str(e))
                raise e from e

        # LLM 호출
        try:
            response = await llm_service.generate(
                prompt=str(request.input),
                functions=functions,
                streaming=False,
            )
        except Exception as e:
            logger.error("LLM 호출 실패", error=str(e))
            raise LLMError(str(e)) from e

        if not isinstance(response, dict):
            raise ValidationError("Unexpected response type")

        # Function Call 처리
        if response.get("function_call"):
            try:
                function_name = response["function_call"].name
                function = registry.get_function(function_name)
                args = json.loads(response["function_call"].arguments)
                result = await function(**args)
                return AgentResponse(result=result)
            except Exception as e:
                logger.error(
                    "함수 실행 실패",
                    function=function_name,
                    error=str(e),
                )
                raise FunctionExecutionError(function_name, e) from e

        return AgentResponse(result=response["content"])

    except Exception as e:
        logger.error("요청 처리 실패", error=str(e))
        raise


@router.post("/chat/stream")
async def chat_stream(
    request: AgentRequest,
    llm_service: OpenAIService = LLM_SERVICE_DEPENDS,
    registry: FunctionRegistry = FUNCTION_REGISTRY_DEPENDS,
) -> EventSourceResponse:
    """LLM과 스트리밍 대화"""

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        try:
            # 요청된 함수들 가져오기
            functions = None
            if request.functions:
                try:
                    functions = [
                        registry.get_function(name) for name in request.functions
                    ]
                except FunctionNotFoundError as e:
                    logger.error("함수를 찾을 수 없음", error=str(e))
                    raise e from e

            # LLM 스트리밍 호출
            try:
                response = await llm_service.generate(
                    prompt=str(request.input),
                    functions=functions,
                    streaming=True,
                )
            except Exception as e:
                logger.error("LLM 호출 실패", error=str(e))
                raise LLMError(str(e)) from e

            if isinstance(response, AsyncIterator):
                async for chunk in response:
                    if chunk.get("content"):
                        yield {"data": chunk["content"]}
                    elif chunk.get("function_call"):
                        try:
                            function_name = chunk["function_call"].name
                            function = registry.get_function(function_name)
                            args = json.loads(chunk["function_call"].arguments)
                            result = await function(**args)
                            yield {"data": str(result)}
                        except Exception as e:
                            logger.error(
                                "함수 실행 실패",
                                function=function_name,
                                error=str(e),
                            )
                            raise FunctionExecutionError(function_name, e) from e
            else:
                raise ValidationError("Unexpected response type")

        except Exception as e:
            logger.error("스트리밍 처리 실패", error=str(e))
            raise

    return EventSourceResponse(event_generator())
