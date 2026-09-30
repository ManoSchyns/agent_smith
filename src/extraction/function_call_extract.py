import re
from .model import ExtractStrategy


class FunctionCallStrategy(ExtractStrategy):

    """Function Call Strategy for extraction"""

    def can_extract(self, llm_output: str) -> bool:
        """
        Is the output of the LLM enclosed in Function call code?
        """
        pattern: str = r"<function_calls>\s*.*?</function_calls>"

        if re.search(pattern, llm_output, re.DOTALL):
            return True

        return False

    def extract(self, llm_output: str) -> str:
        """Extracts the Function call code from the LLM output"""

        if not self.can_extract(llm_output):
            return ""

        tools: list[str] = []

        pattern: str = r"<function_calls>\s*(.*?)</function_calls>"
        codes = re.findall(pattern, llm_output, re.DOTALL)
        for elem in codes:
            if not elem:
                continue

            curr_tool: str = ""
            curr_tool += elem.splitlines()[0].split('"')[1]
            curr_tool += "("

            pattern = r"<parameter\b[^>]*>([\s\S]*?)</parameter>"
            values = re.findall(pattern, elem, re.DOTALL)

            for i, value in enumerate(values):
                try:
                    int(value)
                    curr_tool += value
                except (TypeError, ValueError):
                    if value[0] == '[':
                        curr_tool += value
                    else:
                        curr_tool += str(value)
                if i < len(values) - 1:
                    curr_tool += ","

            curr_tool += ")"
            tools.append(curr_tool)

        return "\n".join(tools)
