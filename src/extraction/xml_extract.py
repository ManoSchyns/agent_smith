import re

from .model import ExtractStrategy


class XMLToolCallStrategy(ExtractStrategy):

    """Extract a function call from XML tool-call output."""

    TOOL_PATTERN = re.compile(
        r"<tool_call>\s*"
        r"<function=(?P<function>[^>]+)>\s*"
        r"(?P<parameters>.*?)"
        r"</function>\s*"
        r"</tool_call>",
        re.DOTALL,
    )

    PARAMETER_PATTERN = re.compile(
        r"<parameter=(?P<name>[^>]+)>\s*"
        r"(?P<value>.*?)"
        r"</parameter>",
        re.DOTALL,
    )

    def can_extract(self, llm_output: str) -> bool:
        """Return True if the output contains an XML tool call."""
        return self.TOOL_PATTERN.search(llm_output) is not None

    def extract(self, llm_output: str) -> str:
        """Extract the function call from XML tool-call output."""

        match = self.TOOL_PATTERN.search(llm_output)

        if match is None:
            return ""

        function_name = match.group("function").strip()
        parameters = match.group("parameters")

        arguments = []

        for parameter in self.PARAMETER_PATTERN.finditer(parameters):
            value = parameter.group("value").strip()

            arguments.append(repr(value))

        return f"{function_name}({', '.join(arguments)})"
