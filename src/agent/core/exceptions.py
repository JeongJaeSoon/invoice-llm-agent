class AgentError(Exception):
    """Agent 기본 예외"""

    pass


class FunctionNotFoundError(AgentError):
    """함수를 찾을 수 없을 때 발생하는 예외"""

    pass


class FunctionExecutionError(AgentError):
    """함수 실행 중 발생하는 예외"""

    pass


class InvalidFunctionError(AgentError):
    """잘못된 함수 정의에 대한 예외"""

    pass


class LLMError(AgentError):
    """LLM 관련 예외"""

    pass
