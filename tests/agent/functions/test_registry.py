import pytest

from src.agent.core.exceptions import FunctionNotFoundError
from src.agent.functions.base import AgentFunction
from src.agent.functions.registry import FunctionRegistry


class TestFunction(AgentFunction):
    """테스트용 함수"""

    name = "test_function"
    description = "테스트 함수입니다."
    parameters = {
        "type": "object",
        "properties": {"param": {"type": "string", "description": "테스트 파라미터"}},
    }

    async def execute(self, **kwargs):
        return kwargs


@pytest.fixture
def registry():
    """레지스트리 fixture"""
    return FunctionRegistry()


def test_register_function(registry):
    """함수 등록 테스트"""
    function = TestFunction()
    registry.register(function)
    assert len(registry.list_functions()) == 1
    assert registry.get_function("test_function") == function


def test_get_nonexistent_function(registry):
    """존재하지 않는 함수 조회 테스트"""
    with pytest.raises(FunctionNotFoundError):
        registry.get_function("nonexistent_function")


def test_list_functions(registry):
    """함수 목록 조회 테스트"""
    function1 = TestFunction()
    function2 = type(
        "TestFunction2",
        (TestFunction,),
        {"name": "test_function2"},
    )()

    registry.register(function1)
    registry.register(function2)

    functions = registry.list_functions()
    assert len(functions) == 2
    assert function1 in functions
    assert function2 in functions
