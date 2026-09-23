from pydantic import ValidationError
from .sandbox_process import worker
from .models import SandboxConfig
import multiprocessing
from multiprocessing import Queue
import json
from typing import Any


class Sandbox:

    def __init__(self, config: str | None = None,
                 connection_mcp: str | None = None,
                 url_connection: str | None = None,
                 file_path: str | None = None):
        self.config = self._load_config(config)

        # Informations nécessaires au worker
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
        Charge la configuration du fichier. En cas d'erreur,
        utilisation de la config par default

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
                json.decoder.JSONDecodeError):
            print("La configuration n'a pas pu etre utilisee."
                  " Utilisation de la configuration par default.")
            return SandboxConfig()

    def deploy(self) -> None:
        """
        Depoie la sandbox en lecture REPL-Style
        """
        while True:

            try:
                command = input(">>> ")

                if command == "exit":
                    break
                else:
                    value = self.execute(command)
                    if value:
                        if isinstance(value, str):
                            print(value)
                        elif value["stdout"]:
                            print(value["stdout"])
                        elif value["stderr"]:
                            print(value["stderr"])
                        elif value["error"]:
                            print(value["error"])

            except (EOFError, KeyboardInterrupt, RuntimeError):
                self.close()
                break

    def execute(self, command: str) -> Any:
        """
        Envoie une commande au worker.
        """

        if not self.process.is_alive():
            raise RuntimeError("Le worker de la sandbox est arrêté.")

        # Envoie la commande
        self.commands.put(command)

        # Attend le résultat
        result = self.results.get()

        return result

    def close(self) -> None:
        """Arrête proprement le worker."""

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
                      connection_mcp="stdio",
                      file_path="mcp_tools_mbpp.py")
    try:
        sandbox.deploy()
    finally:
        sandbox.close()
