import os
import json
from pathlib import Path
import fnmatch


def read_file_tool(filepath: str, start_line: int, end_line: int) -> str:
    """
    Reads the file and returns the lines from start line to end line

    Ars:
        filepath (str): The path to the file
        start_line (int): The index of the starting line to read
        end_line (int): The index of the ending line

    Return:
        (str): A JSON object with the result if successed or not
    """

    if start_line < 0 or end_line < 0:
        return json.dumps({
            "success": False,
            "output": "Error: start_line and end_line must be positive integer"
        })

    try:
        DIRECTORY = os.environ["TESTBED_PATH"]
    except KeyError:
        return json.dumps({
                    "success": False,
                    "output": "Unable to find the folder to work in"
        })

    full_path: str = DIRECTORY + "/" + filepath

    lines: list[str]

    try:
        with open(full_path, "r") as file:
            lines = file.readlines()

    except (FileNotFoundError, PermissionError) as e:
        return json.dumps({
            "success": False,
            "output": str(e)
        })

    lines = lines[start_line:end_line]
    ret_val: str = ""

    for i, line in enumerate(lines):
        ret_val += f"{start_line + i + 1} {line}"

    return json.dumps({
        "success": True,
        "output": ret_val
    })


def edit_file_tool(filepath: str, old_str: str, new_str: str) -> str:
    """
    Edit a file by replacing the old string with the new one.

    Args:
        filepath(str): The file path
        old_str(str): The part to change
        new_str(str): The part to add

    Return:
        A JSON object with the result if successed or not
    """
    try:
        DIRECTORY = os.environ["TESTBED_PATH"]
    except KeyError:
        return json.dumps({
            "success": False,
            "output": "Unable to find the folder to work in"
        })

    full_path: str = DIRECTORY + "/" + filepath

    try:
        with open(full_path, "r") as file:
            content = file.read()

            if old_str not in content:
                return json.dumps({
                    "success": False,
                    "output": f"The content: {old_str}\nCould not be found"
                })
            ret_val = content.replace(old_str, new_str)

        with open(full_path, "w") as file:
            file.write(ret_val)
            return json.dumps({
                "success": True,
                "output": f"The {filepath} file update has "
                "been successfully completed."
            })

    except (FileNotFoundError, PermissionError) as e:
        return json.dumps({
            "success": False,
            "output": str(e)
        })


def list_files_tool(directory: str, pattern: str) -> str:
    """
    Lists the files that match the pattern in the folder.

    Argument:
        Directory (str): the folder to search in
        Pattern (str): the pattern to follow

    Return:
        A JSON object with the result indicating whether
        it was successful or not.
    """
    try:
        root = os.environ["TESTBED_PATH"]
    except KeyError:
        return json.dumps({
            "success": False,
            "output": "Unable to find the folder to work in"
        })
    path = Path(root + "/" + directory)

    all_file = []
    for file in path.rglob("*"):
        if not file.is_file():
            continue

        if not fnmatch.fnmatch(file.name, pattern):
            continue
        all_file.append(f"{file.resolve()}")
    return json.dumps({
        "success": True,
        "output": all_file
    })
