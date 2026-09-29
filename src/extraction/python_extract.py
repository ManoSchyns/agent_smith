import re
from .model import ExtractStrategy


class PythonStrategy(ExtractStrategy):

    """Python Strategy for extraction"""

    def can_extract(self, llm_output: str) -> bool:
        """
        Is the output of the LLM enclosed in Python code?
        """
        pattern: str = r"```python\s*.*?```"

        if re.search(pattern, llm_output, re.DOTALL):
            return True

        return False

    def extract(self, llm_output: str) -> str:
        """Extracts the python code from the LLM output"""

        if not self.can_extract(llm_output):
            return ""

        pattern: str = r"```python\s*(.*?)```"
        codes = re.findall(pattern, llm_output, re.DOTALL)
        return "".join(codes)
