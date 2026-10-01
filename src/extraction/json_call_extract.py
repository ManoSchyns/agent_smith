import json

from .model import ExtractStrategy


class JSONToolCallStrategy(ExtractStrategy):

    """Extract tool calls from JSON instructions."""

    def can_extract(self, llm_output: str) -> bool:
        """Return True if the output contains JSON instructions."""
        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            return False

        return (
            isinstance(data, dict)
            and isinstance(data.get("instructions"), list)
        )

    def extract(self, llm_output: str) -> str:
        """Extract function calls from JSON instructions."""

        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            return ""

        instructions = data.get("instructions", [])
        calls = []

        for instruction in instructions:
            if not isinstance(instruction, dict):
                continue

            function_name = instruction.get("type")
            args = instruction.get("args", {})

            if not function_name or not isinstance(args, dict):
                continue

            arguments = [
                repr(value)
                for value in args.values()
            ]

            calls.append(
                f"{function_name}({', '.join(arguments)})"
            )

        return "\n".join(calls)
