import ast
import re

from .model import ExtractStrategy


class FunctionCallStrategy(ExtractStrategy):

    """Function Call Strategy for extraction."""

    FUNCTION_CALL_PATTERN = re.compile(
        r"<function_calls>\s*(.*?)</function_calls>",
        re.DOTALL,
    )

    FUNCTION_NAME_PATTERN = re.compile(
        r'<function\s*=\s*"([^"]+)"',
    )

    PARAMETER_PATTERN = re.compile(
        r"<parameter\b[^>]*>\s*(.*?)\s*</parameter>",
        re.DOTALL,
    )

    def can_extract(self, llm_output: str) -> bool:
        """Return True if the output contains function calls."""
        return self.FUNCTION_CALL_PATTERN.search(llm_output) is not None

    def extract(self, llm_output: str) -> str:
        """Extract function calls from the LLM output."""

        tools: list[str] = []

        for elem in self.FUNCTION_CALL_PATTERN.findall(llm_output):
            function_match = self.FUNCTION_NAME_PATTERN.search(elem)

            if function_match is None:
                continue

            function_name = function_match.group(1).strip()

            values = self.PARAMETER_PATTERN.findall(elem)

            arguments = [
                self._format_argument(value)
                for value in values
            ]

            tools.append(
                f"{function_name}({', '.join(arguments)})"
            )

        return "\n".join(tools)

    @staticmethod
    def _format_argument(value: str) -> str:
        """Format a parameter as valid Python syntax."""

        value = value.strip()

        try:
            ast.literal_eval(value)
            return value
        except (ValueError, SyntaxError):
            return repr(value)
