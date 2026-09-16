from mcp.server.mcpserver import MCPServer
import sys
from src.mcp.swebench_tools import (
    read_file_tool,
    edit_file_tool,
    list_files_tool,
    search_code_tool,
    search_function_or_class_definition_in_code_tool,
    find_references_tool,
    run_tests_tool,
    get_patch_tool
)


mcp = MCPServer("Agent Smith")


@mcp.tool()
def read_file(filepath: str, start_line: int, end_line: int) -> str:
    """
    Reads the file and returns the lines from start line to end line

    Ars:
        filepath (str): The path to the file
        start_line (int): The index of the starting line to read
        end_line (int): The index of the ending line

    Return:
        (str): A JSON object with the result if successed or not
    """

    return read_file_tool(filepath=filepath,
                          start_line=start_line,
                          end_line=end_line)


@mcp.tool()
def edit_file(filepath: str, old_str: str, new_str: str) -> str:
    """
    Edit a file by replacing the old string with the new one.

    Args:
        filepath(str): The file path
        old_str(str): The part to change
        new_str(str): The part to add

    Return:
        A JSON object with the result if successed or not
    """
    return edit_file_tool(filepath=filepath,
                          old_str=old_str,
                          new_str=new_str)


@mcp.tool()
def list_files(directory: str, pattern: str) -> str:
    """
    Lists the files that match the pattern in the folder.

    Argument:
        Directory (str): the folder to search in
        Pattern (str): the pattern to follow

    Return:
        A JSON object with the result indicating whether
            it was successful or not.
    """
    return list_files_tool(directory=directory, pattern=pattern)


@mcp.tool()
def search_code(pattern: str, file_pattern: str) -> str:
    """
    Searches for a pattern in all files that matches the file_pattern

    Args:
        pattern (str): the pattern to search for
        file_pattern (str): the pattern in the files

    Return:
        A JSON object with the result indicating whether
        it was successful or not.
    """
    return search_code_tool(pattern=pattern,
                            file_pattern=file_pattern)


@mcp.tool()
def search_function_or_class_definition_in_code(name: str) -> str:
    """
    Find the definition of a function or a class

    Arg:
        name (str): the name of the class or function to search for

    Return:
        A JSON object with the result indicating whether
            it was successful or not.
    """
    return search_function_or_class_definition_in_code_tool(
        name=name
    )


@mcp.tool()
def find_references(name: str, filepath: str, line: int) -> str:
    """
    Finds all uses of a class or function defined by the name name

    Arguments:
        name (str): the name of the function/class
        filepath (str): the path to where the class is located
        line (int): the line number where it is located

    Return:
        A JSON object with the result indicating whether
            it was successful or not.
    """
    return find_references_tool(name=name,
                                filepath=filepath,
                                line=line)


@mcp.tool()
def run_tests() -> str:
    """
    Execute the evaulation script

    Return:
        A JSON object with the result if successed or not
    """
    return run_tests_tool()


@mcp.tool()
def get_patch() -> str:
    """
    Retrieve the unified git diff of all changes made to the repository

    Return:
        A JSON object with the result if successed or not and the git diffs
    """
    return get_patch_tool()


if __name__ == "__main__":
    """
    Si on le lance sans args -> stdio
    N importe quel args -> http
    """
    if len(sys.argv) > 1:
        mcp.run(transport="streamable-http",
                host="127.0.0.3")
    else:
        mcp.run(transport="stdio")
