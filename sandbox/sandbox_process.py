
import io
import builtins
import resource

from typing import Any, Callable

from multiprocessing import Queue
from src.mcp.mcp_client import MCPClient

from contextlib import redirect_stdout, redirect_stderr

from .models import SandboxConfig
from .utils import (SAFE_BUILTINS,
                    is_import_allowed, is_path_allowed,
                    get_manual, final_answer,
                    set_memory_limits,
                    set_memory_back)


def worker(
    commands: Queue,
    results: Queue,
    config_dict: dict,
    connection_mcp: str,
    url_connection: str,
    file_path: str
) -> None:
    """
    Main sandbox process
    Executes commands in the secure environment

    Args:
        commands (Queue): The queue of executed commands
        results (Queue): The queue of results
        config_dict: The sandbox configuration
        connection_mcp: The connection type to the MCP server
        url_connection: The URL for connecting to the MCP server
        file_path: The path to the MCP server
    """
    config = SandboxConfig(**config_dict)
    old_soft, old_hard = resource.getrlimit(
        resource.RLIMIT_AS
    )

    def restricted_import(name: str, globals: dict | None = None,
                          locals: dict | None = None,
                          fromlist: tuple = (), level: int = 0) -> Any:
        """
        Redéfinition de la fonction __import__ pour
        vérifier avant chaque import que celui-ci est autorisé
        """
        autorized: list[str] = config.authorized_imports

        if not is_import_allowed(name, autorized):
            raise ImportError(
                f"Import de '{name}' interdit dans la sandbox."
            )

        return builtins.__import__(
            name,
            globals,
            locals,
            fromlist,
            level
        )

    def restricted_open(file: str, *args: Any, **kwargs: Any) -> Any:
        """
        An additional layer has an open function to
        restrict access to files.
        """

        if not is_path_allowed(
            file,
            config.allowed_directories
        ):
            raise PermissionError(
                f"Accès interdit : {file}"
            )

        return open(file, *args, **kwargs)

    # Namespace persistant
    namespace: dict[str, Any] = {
        "__builtins__": {
            **SAFE_BUILTINS,
            "__import__": restricted_import,
            "open": restricted_open
        },
    }

    # Recuperations des tools MCP
    tool_definitions = []

    client_mcp = None

    try:

        if connection_mcp:
            try:
                client_mcp = MCPClient(
                    connection_mcp,
                    file_path=file_path,
                    server_url=url_connection
                )

                client_mcp.connect()

                tool_definitions = client_mcp.list_tools()

                tool_callables: dict[str,
                                     Callable] = client_mcp.get_tools_callable(
                    tool_definitions
                )

                namespace.update(tool_callables)

            except Exception as e:
                print(
                    "La connexion avec le serveur MCP "
                    f"n'a pas pu être établie : {e}"
                )

        # Ajout de final answer
        namespace["final_answer"] = final_answer

        set_memory_limits(config.max_memory_mb, old_hard)
        # Boucle permanente
        while True:

            command = commands.get()

            # Demande d'arrêt
            if command is None:
                break

            # Commande manuel
            if command == "help":
                results.put(get_manual(tool_definitions))
                continue

            try:
                stdout = io.StringIO()
                stderr = io.StringIO()

                with redirect_stdout(stdout), redirect_stderr(stderr):
                    exec(command, namespace)

                results.put({
                    "success": True,
                    "stdout": stdout.getvalue(),
                    "stderr": stderr.getvalue(),
                    "error": None,
                    "kill": False
                })

            except Exception as e:

                results.put({
                    "success": False,
                    "stdout": stdout.getvalue(),
                    "stderr": stderr.getvalue(),
                    "error": str(e),
                    "kill": False
                })

    except (RuntimeError, MemoryError):
        set_memory_back(old_soft, old_hard)
        results.put({
            "success": False,
            "stdout": "",
            "stderr": "",
            "error": "",
            "kill": True
        })
        print("Memory limits exceded.")

    except (EOFError, KeyboardInterrupt):
        pass

    finally:
        if client_mcp:
            client_mcp.close()
