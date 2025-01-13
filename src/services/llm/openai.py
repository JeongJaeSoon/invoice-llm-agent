from typing import Any, AsyncIterator

from openai import AsyncOpenAI
from structlog import get_logger

from src.agent.functions.base import AgentFunction
from src.core.config import settings
from src.services.llm.base import LLMService

logger = get_logger(__name__)


class OpenAIService(LLMService):
    """OpenAI API 서비스"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens

    async def generate(
        self,
        prompt: str,
        functions: list[AgentFunction] | None = None,
        streaming: bool = False,
    ) -> dict[str, Any] | AsyncIterator[dict[str, Any]]:
        """OpenAI API를 사용하여 응답 생성"""
        try:
            if streaming:
                return self._generate_stream(prompt, functions)

            messages = [{"role": "user", "content": prompt}]
            function_definitions = (
                [func.to_dict() for func in functions] if functions else None
            )

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=function_definitions,
                max_tokens=self.max_tokens,
            )

            return {
                "content": response.choices[0].message.content,
                "function_call": response.choices[0].message.function_call,
            }

        except Exception as e:
            logger.error("OpenAI API 호출 실패", error=str(e))
            raise

    async def _generate_stream(
        self, prompt: str, functions: list[AgentFunction] | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """스트리밍 응답 생성"""
        messages = [{"role": "user", "content": prompt}]
        function_definitions = (
            [func.to_dict() for func in functions] if functions else None
        )

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=function_definitions,
                max_tokens=self.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield {"content": content}
                elif chunk.choices[0].delta.function_call:
                    func_call = chunk.choices[0].delta.function_call
                    yield {"function_call": func_call}

        except Exception as e:
            logger.error("OpenAI 스트리밍 API 호출 실패", error=str(e))
            raise
