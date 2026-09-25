from pydantic import ValidationError
from sandbox_process import worker
from models import SandboxConfig
import multiprocessing
from multiprocessing import Queue
from queue import Empty
import json
from typing import Any


class Sandbox:

    """
    A protected sandbox that executes the desired commands
    in a protected environment

    Args:
        config(str): The sandbox configuration
        connection_mcp: The connection type to the MCP server
        url_connection: The URL for connecting to the MCP server
        file_path: The path to the MCP server
    """
    def __init__(self, config: str | None = None,
                 connection_mcp: str | None = None,
                 url_connection: str | None = None,
                 file_path: str | None = None):
        self.config = self._load_config(config)

        self.connection_mcp = connection_mcp
        self.url_connection = url_connection
        self.file_path = file_path

        # Communication avec le worker
        self.commands: Queue = multiprocessing.Queue()
        self.results: Queue = multiprocessing.Queue()

        # Processus permanent
        self.process = multiprocessing.Process(
            target=worker,
            args=(
                self.commands,
                self.results,
                self.config.model_dump(),
                self.connection_mcp,
                self.url_connection,
                self.file_path,
            )
        )

        self.process.start()

    def _load_config(self, config: str | None) -> SandboxConfig:
        """
       Loads the configuration file. In case of error,
        the default configuration is used.

        Arg:
            config(str | None): The configuration to load

        Return:
            SandboxConfig: The configuration class
        """
        if not config:
            return SandboxConfig()

        try:
            with open(config, "r") as file:
                datas = json.load(file)
                return SandboxConfig(**datas)
        except (PermissionError, FileNotFoundError,
                UnicodeDecodeError, ValidationError,
                json.decoder.JSONDecodeError):
            print("The configuration could not be used."
                  " Using the default configuration.")
            return SandboxConfig()

    def deploy(self) -> None:
        """
        Depoie the sandbox in REPL-Style reading mode
        """
        while self.process.is_alive():
            try:
                command = input(">>> ")

                if command == "exit":
                    break

                value = self.execute(command)
                if value:
                    if isinstance(value, str):
                        print(value)
                    else:
                        if value["ended"]:
                            print(value)
                            print("Final answer a ete appele.")
                            break
                        if value["kill"]:
                            break
                        if value["stdout"]:
                            print(value["stdout"])
                        if value["stderr"]:
                            print(value["stderr"])
                        if value["error"]:
                            print(value["error"])

            except (EOFError, KeyboardInterrupt, RuntimeError):
                break
        self.close()

    def execute(self, command: str) -> Any:
        """
        Execute the command in the sandbox

        Arg:
            command (str): La commande

        Return
            Le resultat de la commande
        """

        if not self.process.is_alive():
            raise RuntimeError("The sandbox worker has stopped.")

        # Envoie la commande
        self.commands.put(command)

        try:
            # Attend le résultat
            result = self.results.get(
                timeout=self.config.max_execution_time_seconds
            )
        except Empty:
            self.process.terminate()
            return ("The program did not finish "
                    "within the allotted time.")

        return result

    def close(self) -> None:
        """Stop the sandbox"""

        if self.process.is_alive():

            # Demande au worker de s'arrêter
            self.commands.put(None)

            # Attend sa fermeture
            self.process.join()

        if self.process.is_alive():
            self.process.kill()
            self.process.join()


if __name__ == "__main__":
    sandbox = Sandbox(config="config.json",
                      connection_mcp="http",
                      url_connection="http://127.0.0.3:8000/mcp",
                      file_path="mcp_tools_mbpp.py")
    try:
        sandbox.deploy()
    finally:
        sandbox.close()
