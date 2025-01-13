from typing import AsyncIterator

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from src.agent.core.types import AgentRequest, AgentResponse
from src.services.llm.openai import OpenAIService

router = APIRouter()
llm_service_dependency = Depends(OpenAIService)


@router.post("/chat")
async def chat(
    request: AgentRequest,
    llm_service: OpenAIService = llm_service_dependency,
) -> AgentResponse:
    """LLM과 대화"""
    response = await llm_service.generate(
        prompt=str(request.input),
        streaming=False,
    )
    if isinstance(response, dict):
        return AgentResponse(result=response["content"])
    raise ValueError("Unexpected response type")


@router.post("/chat/stream")
async def chat_stream(
    request: AgentRequest,
    llm_service: OpenAIService = llm_service_dependency,
) -> EventSourceResponse:
    """LLM과 스트리밍 대화"""

    async def event_generator() -> AsyncIterator[dict[str, str]]:
        response = await llm_service.generate(
            prompt=str(request.input),
            streaming=True,
        )
        if isinstance(response, AsyncIterator):
            async for chunk in response:
                if chunk.get("content"):
                    yield {"data": chunk["content"]}

    return EventSourceResponse(event_generator())
