from file_system import list_files_tool
from pathlib import Path
import json
import ast


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
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            continue

    return json.dumps({
        "success": True,
        "output": ret_val
    })


def search_function_or_class_definition_in_code_tool(name: str) -> str:
    """
    Find the definition of a function or a class

    Arg:
        name (str): the name of the class or function to search for

    Return:
        A JSON object with the result indicating whether
            it was successful or not.
    """
    datas = json.loads(list_files_tool("", "*.py"))

    if not datas["success"]:
        return json.dumps({
            "success": False,
            "output": datas["output"]
        })

    ret_val: list[str] = []
    for file_name in datas["output"]:
        try:
            with open(file_name, "r") as file:
                content = file.read()

            tree = ast.parse(content)
            lines = content.splitlines()

            for node in ast.walk(tree):
                if isinstance(node,
                              (ast.FunctionDef, ast.ClassDef,
                               ast.AsyncFunctionDef)):
                    if node.name == name:
                        ret_val.append(
                            f"{file_name}:{node.lineno} "
                            f"{lines[node.lineno - 1]}"
                        )

        except (FileNotFoundError, PermissionError, UnicodeDecodeError,
                SyntaxError):
            continue

    return json.dumps({
            "success": True,
            "output": ret_val
        })


def find_references_tool(name: str, filepath: str, line: int) -> str:
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
    origin: (
        ast.ClassDef | ast.AsyncFunctionDef
        | ast.FunctionDef | None
        ) = get_orginal_ast_obj(name, filepath, line)

    if origin is None:
        return json.dumps({
                "success": False,
                "output": f"The function or class {name} does not exist "
                f"in the file {filepath} "
                f"and on line {line}"
            })

    datas = json.loads(list_files_tool("", "*.py"))
    if not datas["success"]:
        return json.dumps({
            "success": False,
            "output": datas["output"]
        })

    origin_filename = str(Path(filepath).resolve())
    files = datas["output"]
    ret_val: list[str] = []

    for file_name in files:
        try:
            with open(file_name, "r") as file:
                content = file.read()
                tree = ast.parse(content)
        except (FileNotFoundError, PermissionError,
                UnicodeDecodeError, SyntaxError):
            continue

        splited_content = content.splitlines()

        tmp_found: list[str] = []
        imported: bool = False
        if file_name == origin_filename:
            imported = True

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)) and not imported:
                for alias in node.names:
                    if alias.name == origin.name:
                        imported = True

            if (
                isinstance(origin, (ast.AsyncFunctionDef, ast.FunctionDef))
                and is_ref_funct(origin, node)
            ):
                if isinstance(node, (ast.Call, ast.Name)):
                    tmp_found.append(
                        f"{file_name}:{node.lineno} "
                        f"{splited_content[node.lineno - 1]}"
                    )

            elif (
                isinstance(origin, ast.ClassDef)
                and is_ref_class(origin, node)
            ):
                if isinstance(node, (ast.Call, ast.Name, ast.ClassDef)):
                    tmp_found.append(
                        f"{file_name}:{node.lineno} "
                        f"{splited_content[node.lineno - 1]}"
                    )

        if imported:
            ret_val.extend(tmp_found)

    return json.dumps({
        "success": True,
        "output": ret_val
    })


def is_ref_funct(ref: ast.FunctionDef | ast.AsyncFunctionDef,
                 node: ast.AST) -> bool:
    """
    Indicates whether the node is a reference to the ref function.

    Argument:
        ref(ast.ClassDef):: the base reference
        node(ast.AST):: the node to check

    Return:
        True if it is indeed a reference
        False otherwise
    """
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == ref.name:
            return True
    elif (
        isinstance(node, ast.Name)
        and node.id == ref.name
        and isinstance(node.ctx, ast.Load)
    ):
        return True
    return False


def is_ref_class(ref: ast.ClassDef, node: ast.AST) -> bool:
    """
    Indicates whether the node is a reference to the ref class.

    Argument:
        ref(ast.ClassDef):: the base reference
        node(ast.AST):: the node to check

    Return:
        True if it is indeed a reference
        False otherwise
    """
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == ref.name:
            return True
    elif isinstance(node, ast.ClassDef):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == ref.name:
                return True

    elif (
        isinstance(node, ast.Name)
        and node.id == ref.name
        and isinstance(node.ctx, ast.Load)
    ):
        return True
    return False


def get_orginal_ast_obj(name: str, filepath: str, line: int) -> (
        ast.AsyncFunctionDef
        | ast.FunctionDef
        | ast.ClassDef
        | None
        ):
    """
    Retrieve the AST object corresponding to the searched object

    Args:
        name (str): the name of the searched resource
        filepath (str): the path to the file
        line (int): the line number in the file

    Return:
        ast.AST: The AST object corresponding to the search
        None if not found
    """
    try:
        with open(filepath, "r") as file:
            content = file.read()

        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.FunctionDef, ast.ClassDef,
                       ast.AsyncFunctionDef)
            ):
                if node.lineno == line and node.name == name:
                    return node
        return None
    except (FileNotFoundError, PermissionError,
            UnicodeDecodeError, SyntaxError):
        return None


if __name__ == "__main__":
    datas = json.loads(find_references_tool(
        "find_references_tool",
        "src/mcp/swebench_tools/code_seach.py", 97))

    if datas["success"]:
        for lin in datas["output"]:
            print(lin)
    else:
        print(datas["output"])
