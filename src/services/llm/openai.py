from typing import Any, AsyncIterator

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion
from structlog import get_logger

from src.agent.functions.base import AgentFunction
from src.core.config import settings
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

            message = completion.choices[0].message
            return {
                "content": message.content or "",
                "function_call": message.function_call,
            }

        except Exception as e:
            logger.error("OpenAI API 호출 실패", error=str(e))
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
            stream = await self.client.chat.completions.create(**params)

            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield {"content": delta.content}
                elif delta.function_call:
                    yield {"function_call": delta.function_call}

        except Exception as e:
            logger.error("OpenAI 스트리밍 API 호출 실패", error=str(e))
            raise
