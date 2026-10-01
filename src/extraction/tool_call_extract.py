import re

from .model import ExtractStrategy


class ToolCallStartEndStrategy(ExtractStrategy):

    """Extract tool calls enclosed by tool_call_start/end tags."""

    TOOL_CALL_PATTERN = re.compile(
        r"<\|tool_call_start\|>\s*\[(.*?)\]\s*<\|tool_call_end\|>",
        re.DOTALL,
    )

    FUNCTION_CALL_PATTERN = re.compile(
        r"\b([a-zA-Z_]\w*)\s*\(.*?\)"
    )

    def can_extract(self, llm_output: str) -> bool:
        """Return True if the output contains a tool call."""
        return self.TOOL_CALL_PATTERN.search(llm_output) is not None

    def extract(self, llm_output: str) -> str:
        """Extract individual tool calls from the LLM output."""

        calls: list[str] = []

        for block in self.TOOL_CALL_PATTERN.findall(llm_output):
            calls.extend(
                match.group(0)
                for match in self.FUNCTION_CALL_PATTERN.finditer(block)
            )

        return "\n".join(calls)
