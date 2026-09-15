from .file_system import list_files_tool
import json


def search_code_tool(pattern: str, file_pattern: str) -> str:
    """
    Searches for a pattern in all files that matches the file_pattern

    Args:
        pattern (str): the pattern to search for
        file_pattern (str): the pattern in the files

    Return:
        A JSON object with the result indicating whether
        it was successful or not.
    """

    datas = json.loads(list_files_tool("", file_pattern))

    if not datas["success"]:
        return json.dumps({
            "success": False,
            "output": datas["output"]
        })

    files = datas["output"]

    ret_val: list[str] = []
    for file_name in files:

        try:
            with open(file_name, "r") as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if pattern in line:
                    ret_val.append(f"{file_name}:{i + 1} {line}")
        except (FileNotFoundError, PermissionError):
            continue

    return json.dumps({
        "success": True,
        "output": ret_val
    })


if __name__ == "__main__":
    value = json.loads(search_code_tool("DIRECTORY", "*.py"))
    lines = value["output"]
    for line in lines:
        print(line)
