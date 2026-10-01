import json

from .model import ExtractStrategy


class JSONFunctionCallStrategy(ExtractStrategy):

    """Extract function calls from JSON output."""

    def can_extract(self, llm_output: str) -> bool:
        """Return True if the output contains a JSON function call."""

        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            return False

        return (
            isinstance(data, dict)
            and isinstance(data.get("name"), str)
            and isinstance(data.get("parameters"), dict)
        )

    def extract(self, llm_output: str) -> str:
        """Extract the function call from JSON output."""

        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            return ""

        function_name = data.get("name")
        parameters = data.get("parameters")

        if not isinstance(function_name, str):
            return ""

        if not isinstance(parameters, dict):
            return ""

        arguments = ", ".join(
            f"{name}={value!r}"
            for name, value in parameters.items()
        )

        return f"{function_name}({arguments})"
