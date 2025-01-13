from typing import AsyncIterator, Final

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from src.agent.core.types import AgentRequest, AgentResponse
from src.agent.functions.registry import FunctionRegistry
from src.services.llm.openai import OpenAIService

router = APIRouter()


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
    # 요청된 함수들 가져오기
    functions = None
    if request.functions:
        functions = [registry.get_function(name) for name in request.functions]

    # LLM 호출
    response = await llm_service.generate(
        prompt=str(request.input),
        functions=functions,
        streaming=False,
    )

    if not isinstance(response, dict):
        raise ValueError("Unexpected response type")

    # Function Call 처리
    if response.get("function_call"):
        function_name = response["function_call"].name
        function = registry.get_function(function_name)
        args = response["function_call"].arguments
        result = await function.execute(**args)
        return AgentResponse(result=result)

    return AgentResponse(result=response["content"])


@router.post("/chat/stream")
async def chat_stream(
    request: AgentRequest,
    llm_service: OpenAIService = LLM_SERVICE_DEPENDS,
    registry: FunctionRegistry = FUNCTION_REGISTRY_DEPENDS,
) -> EventSourceResponse:
    """LLM과 스트리밍 대화"""

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        # 요청된 함수들 가져오기
        functions = None
        if request.functions:
            functions = [registry.get_function(name) for name in request.functions]

        # LLM 스트리밍 호출
        response = await llm_service.generate(
            prompt=str(request.input),
            functions=functions,
            streaming=True,
        )

        if isinstance(response, AsyncIterator):
            async for chunk in response:
                if chunk.get("content"):
                    yield {"data": chunk["content"]}
                elif chunk.get("function_call"):
                    function_name = chunk["function_call"].name
                    function = registry.get_function(function_name)
                    args = chunk["function_call"].arguments
                    result = await function.execute(**args)
                    yield {"data": str(result)}

    return EventSourceResponse(event_generator())
