from .model import ExtractStrategy, ExtractError
from .python_extract import PythonStrategy
from .function_call_extract import FunctionCallStrategy
from .json_call_extract import JSONToolCallStrategy
from .tool_call_extract import ToolCallStartEndStrategy
from .xml_extract import XMLToolCallStrategy
from .json_call_extract_2 import JSONFunctionCallStrategy
from .json_call_extract_3 import JSONStepsStrategy
from .json_call_extract_4 import JSONActionStrategy


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
        FunctionCallStrategy(),
        JSONToolCallStrategy(),
        ToolCallStartEndStrategy(),
        XMLToolCallStrategy(),
        JSONFunctionCallStrategy(),
        JSONStepsStrategy(),
        JSONActionStrategy()
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
