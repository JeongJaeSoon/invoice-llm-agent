from typing import Any, Dict

from src.agent.core.agent_function import AgentFunction


class CalculateFunction(AgentFunction):
    name = "calculate"
    description = "주어진 수학 표현식을 계산합니다."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "계산할 수학 표현식 (예: '2 + 2', '10 * 5')",
            }
        },
        "required": ["expression"],
    }

    async def execute(self, **kwargs: Dict[str, Any]) -> Any:
        """수학 표현식을 안전하게 계산합니다."""
        expression = str(kwargs.get("expression", ""))
        try:
            # 안전한 계산을 위해 제한된 연산자만 허용
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("허용되지 않는 문자가 포함되어 있습니다.")

            # eval을 사용하여 계산 (제한된 문자만 허용되므로 안전)
            result = eval(expression)
            return {"result": result}
        except Exception as e:
            raise ValueError(f"계산 중 오류 발생: {str(e)}") from e
