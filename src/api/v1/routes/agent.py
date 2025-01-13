from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from src.agent.core.types import AgentRequest, AgentResponse
from src.services.llm.openai import OpenAIService

router = APIRouter()

# 의존성 주입을 위한 함수
llm_service_dependency = Depends(OpenAIService)


@router.post("/chat")
async def chat(
    request: AgentRequest,
    llm_service: OpenAIService = llm_service_dependency,
) -> AgentResponse:
    """LLM과 대화"""
    response = await llm_service.generate(
        prompt=request.input,
        streaming=False,
    )
    return AgentResponse(result=response["content"])


@router.post("/chat/stream")
async def chat_stream(
    request: AgentRequest,
    llm_service: OpenAIService = llm_service_dependency,
):
    """LLM과 스트리밍 대화"""

    async def event_generator():
        async for chunk in await llm_service.generate(
            prompt=request.input,
            streaming=True,
        ):
            if "content" in chunk:
                yield {"data": chunk["content"]}

    return EventSourceResponse(event_generator())
