from pathlib import Path


# Safe Builtins allowed
SAFE_BUILTINS = {
    "bool": bool,
    "int": int,
    "float": float,
    "complex": complex,
    "str": str,
    "bytes": bytes,
    "bytearray": bytearray,
    "list": list,
    "tuple": tuple,
    "dict": dict,
    "set": set,
    "frozenset": frozenset,
    "range": range,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "iter": iter,
    "next": next,
    "reversed": reversed,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "divmod": divmod,
    "len": len,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "type": type,
    "callable": callable,
    "repr": repr,
    "format": format,
    "ord": ord,
    "chr": chr,
    "bin": bin,
    "hex": hex,
    "print": print,
    "id": id,
    "hash": hash,
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "RuntimeError": RuntimeError,
    "AttributeError": AttributeError,
    "ImportError": ImportError,
    "FileNotFoundError": FileNotFoundError,
    "PermissionError": PermissionError,
}


# Forbideb import for Internet Connections
FORBIDEN_IMPORTS = [
    "socket",
    "ssl",
    "http",
    "urllib",
    "ftplib",
    "smtplib",
    "imaplib",
    "poplib",
    "telnetlib",
    "xmlrpc",
    "requests",
    "urllib3",
    "httpx",
    "aiohttp",
]


def is_import_forbidden(name: str) -> bool:
    """
    Checks if the attempted import is allowed or not

    Args:
        name (str): The import

    Return
        True / False if allowed or not
    """
    for forbidden in FORBIDEN_IMPORTS:

        if forbidden.endswith(".*"):
            prefix = forbidden[:-2]

            if name == prefix or name.startswith(prefix + "."):
                return True

        elif name == forbidden:
            return True

    return False


def is_import_allowed(name: str, authorized_imports: list[str]) -> bool:
    """
    Checks if name is in the list of allowed imports

    Args:
        name (str): the import to check
        authorized_imports (list[str]): the allowed imports

    Return:
        True / False depending on whether the import is allowed
    """

    if is_import_forbidden(name):
        return False

    for allowed in authorized_imports:

        if allowed.endswith(".*"):
            prefix = allowed[:-2]

            if name == prefix or name.startswith(prefix + "."):
                return True

        elif name == allowed:
            return True

    return False


def is_path_allowed(
        path_file: str,
        allowed_directories: list[str]
        ) -> bool:
    """
    Determines if the file is allowed in the sandbox

    Args:
        path_file (str): The file name
        allowed_directories (list): The allowed paths

    Return:
        True / False if it is allowed or not
    """

    try:
        path = Path(path_file).resolve()

        for directory_name in allowed_directories:
            directory = Path(directory_name).resolve()

            try:
                path.relative_to(directory)
                return True
            except ValueError:
                continue

        return False

    except (OSError, RuntimeError):
        return False


def get_manual(tools: list) -> str:
    """
    Return the manual for a given list of tools

    Arg:
        tools(list): The specified tools

    Return:
        (str): The description of each tool
    """

    manual = ""

    for tool in tools:
        manual += f"\nFunction: {tool.name}\n"
        manual += f"{tool.description}\n"
        manual += "===================\n"

    manual += f"\nFunction: {final_answer.__name__}\n"
    manual += f"{final_answer.__doc__}\n"
    manual += "===================\n"

    return manual


def final_answer() -> None:
    "test"
    print("nice")
