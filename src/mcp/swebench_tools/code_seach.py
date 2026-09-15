from file_system import list_files_tool
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


def search_function_or_class_definition_in_code_tool(name) -> str:
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
                        ret_val.append(f"{file_name}:{node.lineno} {lines[node.lineno - 1]}")

        except (FileNotFoundError, PermissionError, UnicodeDecodeError,
                SyntaxError):
            continue

    return json.dumps({
            "success": True,
            "output": ret_val
        })


def find_references(name: str, filepath: str, line: int) -> str:
    """
    Finds all uses of a class or function defined by the name `name`

    Arguments:
        name (str): the name of the function/class
        filepath (str): the path to where the class is located
        line (int): the line number where it is located

    Return:
        A JSON object with the result indicating whether
            it was successful or not.
    """
    origin: ast.AST = get_orginal_ast_obj(name, filepath, line)

    if isinstance(origin, (ast.AsyncFunctionDef, ast.FunctionDef)):
        # start function
        pass

    elif isinstance(origin, ast.ClassDef):
        # start class
        pass

    return json.dumps({
        "success": False,
        "output": f"The class or function bearing the name: {name}"
                  f"could not be found in the file: {filepath}"
                  f"at the line: {line}"
        })


def find_ref_funct(ref: ast.FunctionDef) -> str:
    """
    Recherche toutes les references a une fonction dans les fichiers

    Arg:
        ref (ast.FunctionDef): la definition de la fonction

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
    
    files = datas["output"]
    
    ret_val: list[str] = []
    for file_name in files:
    
        try:
            with open(file_name, "r") as file:
                # analyser les imports
                # Regarder les appels si ce sont des Call ou Ref
                # verifier aussi le ctx + nom
                # Si tout bon -> C est ma fonction
                pass
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            continue
    
    return json.dumps({
        "success": True,
        "output": ret_val
    })



def get_orginal_ast_obj(name: str, filepath: str, line: int) -> ast.AST | None:
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
            if isinstance(node,(ast.FunctionDef, ast.ClassDef,
                                ast.AsyncFunctionDef)):
                if node.lineno == line and node.name == name:
                    return node
        return None
    except (FileNotFoundError, PermissionError, UnicodeDecodeError,
                    SyntaxError) as e:
        return None

if __name__ == "__main__":
    find_references("connect", "src/mcp/mcp_client/client.py", 48)
