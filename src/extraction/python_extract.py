import re


def is_python_extract(llm_output: str) -> bool:
    """
    Is the output of the LLM enclosed in Python code?

    Args:
        llm_output(str): The output of the LLM

    Return:
        True / False if the extraction strategy is Python
    """
    pattern: str = r"```python\s*.*?```"

    if re.search(pattern, llm_output, re.DOTALL):
        return True

    return False


def python_extract(llm_output: str) -> str:
    """
    Extracts the code from the LLM output

    Args:
        llm_output(str): The LLM output

    Return:
        str: The code
    """

    pattern: str = r"```python\s*(.*?)```"
    codes = re.findall(pattern, llm_output, re.DOTALL)
    return "".join(codes)
