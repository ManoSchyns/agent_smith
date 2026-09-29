from .model import ExtractStrategy, ExtractError
from .python_extract import PythonStrategy
from .tool_call_extract_1 import ToolCallStrategyFirst


def extract_code(llm_output: str) -> str:
    """
    Extracts the output code from the LLM

    Arg:
        llm_output(str): The output of the LLM

    Return
        str: The return code
    """
    strategies: list[ExtractStrategy] = [
        PythonStrategy(),
        ToolCallStrategyFirst()
    ]
    code: str = extraction(strategies, llm_output)
    if not code.strip():
        raise ExtractError("No code could be extracted")

    return code


def extraction(strategies: list[ExtractStrategy], llm_output: str) -> str:
    """
    Try extracting the code for each strategy.

    Args:
        strategies: The extraction strategies
        Llm_output: The LLM output

    Return:
        The code
    """
    code: str = ""
    for strat in strategies:
        if strat.can_extract(llm_output):
            code += strat.extract(llm_output)
    return code
