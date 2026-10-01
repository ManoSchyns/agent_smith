import json

from .model import ExtractStrategy


class JSONActionStrategy(ExtractStrategy):

    """Extract function calls from JSON action objects."""

    def can_extract(self, llm_output: str) -> bool:
        """Return True if the output contains JSON actions."""

        for line in llm_output.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if (
                isinstance(data, dict)
                and isinstance(data.get("action"), str)
            ):
                return True

        return False

    def extract(self, llm_output: str) -> str:
        """Extract function calls from JSON action objects."""

        calls: list[str] = []

        for line in llm_output.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(data, dict):
                continue

            function_name = data.get("action")

            if not isinstance(function_name, str):
                continue

            arguments = ", ".join(
                f"{name}={value!r}"
                for name, value in data.items()
                if name != "action"
            )

            calls.append(
                f"{function_name}({arguments})"
            )

        return "\n".join(calls)
