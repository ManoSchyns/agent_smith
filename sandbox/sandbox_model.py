from pydantic import BaseModel, Field, ValidationError
from src.mcp.mcp_client import MCPClient
import multiprocessing
import json


class SandboxConfig(BaseModel):
    """Sandbox configuration for student solutions.
    Uses allowlist approach: only imports in authorized_imports are allowed.
    Everything else is blocked by default.
    """

    authorized_imports: list[str] = Field(default_factory=lambda: [
    "math", "math.*",
    "collections", "collections.*",
    "itertools", "re", "json",
    "typing", "typing.*",
    "functools", "operator",
    "heapq", "bisect", "copy",
    "string", "random",
    "datetime", "datetime.*",
    "array", "cmath",
    ])

    allowed_directories: list[str] = Field(default_factory=lambda: [
    "/testbed", "/tmp/agent"
    ])

    max_execution_time_seconds: int = 30
    max_memory_mb: int = 51

class Sandbox:

    def __init__(self, config: str | None = None,
                 connection_mcp: str | None = None,
                 url_connection: str | None = None,
                 file_path: str | None = None):
        self.config = self._load_config(config)

        self.namespace: dict = {}

        self.client_mcp: MCPClient | None = None
        self.tools: list | None = None
        if connection_mcp:
            try:
                self.client_mcp = MCPClient(connection_mcp,
                                            file_path=file_path,
                                            server_url=url_connection)
                self.client_mcp.connect()
                self.tools = self.client_mcp.list_tools()

                self.namespace = self.client_mcp.get_tools_callable(self.tools)
            except Exception:
                self.client_mcp = None
                print("La connection avec le serveur MCP n'a pas pu etre etablie")

        self.namespace["final_answer"] = final_answer


    def _load_config(self, config: str | None) -> SandboxConfig:
        """
        Charge la configuration du fichier. En cas d'erreur, utilisation de la config par default

        Arg:
            config (str | None): La config a charger

        Return:
            SandboxConfig: La classe de configuration
        """
        if not config:
            return SandboxConfig()

        try:
            with open(config, "r") as file:
                datas = json.load(file)
                return SandboxConfig(**datas)
        except (PermissionError, FileNotFoundError,
                UnicodeDecodeError, ValidationError,
                json.decoder.JSONDecodeError) as e:
            print("La configuration n'a pas pu etre utilisee."
                  " Utilisation de la configuration par default.")
            return SandboxConfig()

    def get_manual(self):
        manual: str = ""

        if self.tools:
            for tool in self.tools:
                manual += f"\nFunction: {tool.name}\n"
                manual += f"{tool.description}\n"
                manual += "==================="
        manual += f"\nFunction: {final_answer.__name__}\n"
        manual += f"{final_answer.__doc__}\n"
        manual += "==================="
        return manual

    def deploy(self):
        # lecture en REPL-style
        while True:

            try:
                command = input(">>> ")

                if command == "exit":
                    break

                elif command == "help()":
                    manual = self.get_manual()
                    print(manual)
                else:
                    self.execute(command)
            except (EOFError, KeyboardInterrupt, RuntimeError):
                self.close()
                break

    def execute(self, command: str):
        # executer du code et verifier les imports
        try:
            exec(command, self.namespace)
        except Exception as e:
            print(e)

    def close(self) -> None:
        if self.client_mcp:
            self.client_mcp.close()
            self.client_mcp = None

def final_answer():
    "test"
    print("nice")


if __name__ == "__main__":
    sandbox = Sandbox(config="config.json",
        connection_mcp="stdio",
            file_path="mcp_tools_swebench.py")
    sandbox.deploy()
    sandbox.close()