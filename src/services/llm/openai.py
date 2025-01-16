"""OpenAI API 서비스"""

import time
from typing import Any, AsyncIterator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion
from structlog import get_logger

from src.agent.functions.base import AgentFunction
from src.core.config import settings
from src.core.metrics import (
    LLM_API_ERRORS,
    LLM_API_LATENCY,
    LLM_API_REQUESTS,
    LLM_TOKEN_USAGE,
)
from src.services.llm.base import LLMService

logger = get_logger(__name__)


class OpenAIService(LLMService):
    """OpenAI API 서비스"""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens

    async def generate(
        self,
        prompt: str,
        functions: list[AgentFunction] | None = None,
        streaming: bool = False,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        try:
            if streaming:
                return self._generate_stream(prompt, functions)

            start_time = time.time()
            LLM_API_REQUESTS.labels(model=self.model).inc()

            messages: list[ChatCompletionMessageParam] = [
                {"role": "user", "content": prompt}
            ]

            params: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
            }

            if functions:
                tools = [
                    {"type": "function", "function": func.to_dict()}
                    for func in functions
                ]
                params["tools"] = tools

            completion: ChatCompletion = await self.client.chat.completions.create(
                **params
            )

            # 토큰 사용량 메트릭 수집
            if completion.usage:
                LLM_TOKEN_USAGE.labels(model=self.model, usage_type="prompt").inc(
                    completion.usage.prompt_tokens
                )
                LLM_TOKEN_USAGE.labels(model=self.model, usage_type="completion").inc(
                    completion.usage.completion_tokens
                )

            # 응답 시간 메트릭 수집
            duration = time.time() - start_time
            LLM_API_LATENCY.labels(model=self.model).observe(duration)

            message = completion.choices[0].message
            return {
                "content": message.content or "",
                "function_call": message.function_call,
            }

        except Exception as e:
            logger.error("OpenAI API 호출 실패", error=str(e))
            LLM_API_ERRORS.labels(
                model=self.model,
                error_type=type(e).__name__,
            ).inc()
            raise

    async def _generate_stream(
        self, prompt: str, functions: list[AgentFunction] | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        messages: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": prompt}
        ]

        params: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "stream": True,
        }

        if functions:
            tools = [
                {"type": "function", "function": func.to_dict()} for func in functions
            ]
            params["tools"] = tools

        try:
            start_time = time.time()
            LLM_API_REQUESTS.labels(model=self.model).inc()

            stream = await self.client.chat.completions.create(**params)

            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield {"content": delta.content}
                elif delta.function_call:
                    yield {"function_call": delta.function_call}

            # 응답 시간 메트릭 수집
            duration = time.time() - start_time
            LLM_API_LATENCY.labels(model=self.model).observe(duration)

        except Exception as e:
            logger.error("OpenAI 스트리밍 API 호출 실패", error=str(e))
            LLM_API_ERRORS.labels(
                model=self.model,
                error_type=type(e).__name__,
            ).inc()
            raise
