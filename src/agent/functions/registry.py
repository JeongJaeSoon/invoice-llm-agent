import importlib
import pkgutil
from typing import Dict

from structlog import get_logger

from src.agent.core.exceptions import FunctionNotFoundError
from src.agent.functions.base import AgentFunction

logger = get_logger(__name__)


class FunctionRegistry:
    """Agent 함수 레지스트리"""

    def __init__(self) -> None:
        self._functions: Dict[str, AgentFunction] = {}

    def register(self, function: AgentFunction) -> None:
        """함수 등록"""
        logger.info(
            "함수 등록",
            name=function.name,
            description=function.description,
        )
        self._functions[function.name] = function

    def get_function(self, name: str) -> AgentFunction:
        """함수 조회"""
        if name not in self._functions:
            raise FunctionNotFoundError(f"Function {name} not found")
        return self._functions[name]

    def list_functions(self) -> list[AgentFunction]:
        """등록된 모든 함수 목록"""
        return list(self._functions.values())

    @classmethod
    def load_functions(cls) -> "FunctionRegistry":
        """모듈에서 자동으로 함수 로드"""
        registry = cls()

        # functions/modules 디렉토리의 모든 모듈을 검색
        modules_path = "src.agent.functions.modules"
        try:
            package = importlib.import_module(modules_path)
            for _, name, _ in pkgutil.iter_modules(
                package.__path__,
                f"{modules_path}.",
            ):
                try:
                    module = importlib.import_module(name)
                    # AgentFunction 인스턴스 검색 및 등록
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, AgentFunction):
                            registry.register(attr)
                except Exception as e:
                    logger.error(
                        "모듈 로드 실패",
                        module=name,
                        error=str(e),
                    )
        except Exception as e:
            logger.error("함수 로드 실패", error=str(e))

        return registry
