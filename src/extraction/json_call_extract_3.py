import json

from .model import ExtractStrategy


class JSONStepsStrategy(ExtractStrategy):

    """Extract function calls from JSON steps."""

    def can_extract(self, llm_output: str) -> bool:
        """Return True if the output contains JSON steps."""

        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            return False

        return (
            isinstance(data, dict)
            and isinstance(data.get("steps"), list)
        )

    def extract(self, llm_output: str) -> str:
        """Extract function calls from JSON steps."""

        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            return ""

        steps = data.get("steps", [])

        if not isinstance(steps, list):
            return ""

        calls: list[str] = []

        for step in steps:
            if not isinstance(step, dict):
                continue

            function_name = step.get("action")

            if not isinstance(function_name, str):
                continue

            arguments = ", ".join(
                f"{name}={value!r}"
                for name, value in step.items()
                if name != "action"
            )

            calls.append(
                f"{function_name}({arguments})"
            )

        return "\n".join(calls)
