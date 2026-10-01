import subprocess
import json
import ast
import os

from .file_system import list_files_tool


def get_container_id() -> str | None:
    """
    Retrieve the container ID from the environment.
    """
    try:
        return os.environ["CONTAINER_ID"]
    except KeyError:
        return None


def read_container_file(filepath: str) -> str | None:
    """
    Read a text file from the Docker container.
    """

    container_id = get_container_id()

    if container_id is None:
        return None

    result = subprocess.run(
        [
            "docker",
            "exec",
            container_id,
            "cat",
            filepath
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    return result.stdout


def search_code_tool(pattern: str, file_pattern: str) -> str:
    """
    Searches for a pattern in all files matching file_pattern.
    """

    datas = json.loads(list_files_tool("", file_pattern))

    if not datas["success"]:
        return json.dumps({
            "success": False,
            "output": datas["output"]
        })

    ret_val: list[str] = []

    for file_name in datas["output"]:
        content = read_container_file(file_name)

        if content is None:
            continue

        for i, line in enumerate(content.splitlines()):
            if pattern in line:
                ret_val.append(
                    f"{file_name}:{i + 1} {line}"
                )

    return json.dumps({
        "success": True,
        "output": ret_val
    })


def search_function_or_class_definition_in_code_tool(name: str) -> str:
    """
    Find the definition of a function or a class.
    """

    datas = json.loads(list_files_tool("", "*.py"))

    if not datas["success"]:
        return json.dumps({
            "success": False,
            "output": datas["output"]
        })

    ret_val: list[str] = []

    for file_name in datas["output"]:
        content = read_container_file(file_name)

        if content is None:
            continue

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        lines = content.splitlines()

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.ClassDef,
                    ast.AsyncFunctionDef
                )
            ):
                if node.name == name:
                    ret_val.append(
                        f"{file_name}:{node.lineno} "
                        f"{lines[node.lineno - 1]}"
                    )

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

    files = datas["output"]
    ret_val: list[str] = []

    for file_name in files:
        content = read_container_file(file_name)

        if content is None:
            continue

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        splited_content = content.splitlines()

        tmp_found: list[str] = []
        imported: bool = False
        if file_name == filepath:
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
        content = read_container_file(filepath)
        if content is None:
            return None

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
