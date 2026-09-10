from .python_extract import is_python_extract, python_extract


class ExtractError(Exception):
    """
    Error handling for extraction
    """
    pass


def extract_code(llm_output: str) -> str:
    """
    Extracts the output code from the LLM

    Arg:
        llm_output(str): The output of the LLM

    Return
        str: The return code
    """
    if is_python_extract(llm_output):
        return python_extract(llm_output)
    else:
        raise ExtractError(
            "No extraction method "
            "does not allow obtaining the code or there is no "
            f"code of everything in the output: {llm_output}"
        )
