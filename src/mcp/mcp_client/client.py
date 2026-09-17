from typing import Any, Callable
import asyncio
import threading
import os

import httpx
from mcp import ClientSession, StdioServerParameters, MCPError
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client


class MCPClientError(Exception):
    """
    Error class MCPCLIENT
    """
    pass


class MCPClient:
    """
    The MCP client.
    For connections to servers via STDIO or HTTP.

    Args:
        transport (str): STDIO or HTTP
        file_path (str | None): le chemin vers le fichier pour stdio
        server_url (str | None): l'url vers le server mcp
    """

    def __init__(
        self,
        transport: str,
        file_path: str | None = None,
        server_url: str | None = None,
    ):
        self.transport = transport

        self.server_command = "uv"

        self.file_path = file_path
        if file_path and file_path.endswith(".py"):
            self.command = ["run", "python", file_path]
        else:
            self.command = []

        self.server_url = server_url

        # MCP objects
        self.session: ClientSession | None = None
        self._exit_stack = None

        # Thread / Event Loop
        self.loop: asyncio.AbstractEventLoop | None = None
        self.thread: threading.Thread | None = None

        # Synchronisation
        self.loop_ready = threading.Event()
        self.connected = threading.Event()

        # Error from the MCP thread
        self._error: Exception | None = None

        self._shutdown_event: asyncio.Event | None = None

    def _run_loop(self) -> None:
        """
        Entry point of the MCP thread. And set the event loop
        """

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop_ready.set()

        try:
            self.loop.run_until_complete(
                self._connection_loop()
            )

        except Exception as e:
            self._error = e

        finally:
            self.loop.close()

    def start_loop(self) -> None:
        """
        Start the MCP thread and its event loop.
        """

        if self.thread is not None:
            return

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
        )

        self.thread.start()

        self.loop_ready.wait()

    async def _connection_loop(self) -> None:
        """
        Owns the MCP connection for its entire lifetime.

        The connection is created, used and closed
        inside the same async context.
        """

        self._shutdown_event = asyncio.Event()

        if self.transport == "http":

            if self.server_url is None:
                raise MCPClientError(
                    "server_url is required for HTTP"
                )

            async with streamable_http_client(
                self.server_url
            ) as streams:
                read, write, *_ = streams

                async with ClientSession(
                    read,
                    write
                ) as session:

                    self.session = session

                    await self.session.initialize()

                    self.connected.set()

                    # Keep the connection alive
                    await self._shutdown_event.wait()

        elif self.transport == "stdio" and self.command:

            server_params = StdioServerParameters(
                command=self.server_command,
                args=self.command,
                env=os.environ.copy()
            )

            async with stdio_client(
                server_params
            ) as streams:

                read, write = streams

                async with ClientSession(
                    read,
                    write
                ) as session:

                    self.session = session

                    await self.session.initialize()

                    self.connected.set()

                    # Keep the connection alive
                    await self._shutdown_event.wait()

        else:
            raise MCPClientError(
                f"Transport inconnu : {self.transport}"
            )

        self.session = None

    def _run_async(self, coro: Any) -> Any:
        """
        Execute an async coroutine inside the MCP event loop
        and wait synchronously for its result.

        Arg:
            coro: The cocoutine

        Return:
            Any -> the output of the coroutine
        """

        if self.loop is None:
            raise MCPClientError(
                "Event loop not started"
            )

        future = asyncio.run_coroutine_threadsafe(
            coro,
            self.loop,
        )

        return future.result()

    def connect(self) -> None:
        """
        Start the MCP thread and wait until the connection
        is ready.
        """

        if self.connected.is_set():
            return

        self.start_loop()

        self.connected.wait(timeout=5)

        if self._error is not None:
            raise MCPClientError(
                "Erreur MCP : The connection could not be established."
            )

    async def _list_tools(self) -> Any:
        """
        Async implementation of list_tools.
        """

        if self.session is None:
            raise MCPClientError(
                "Client not logged in"
            )

        result = await self.session.list_tools()

        return result.tools

    def list_tools(self) -> Any:
        """
        Synchronous interface for list_tools.
        """

        return self._run_async(
            self._list_tools()
        )

    def make_callable(
        self,
        name: str,
    ) -> Callable:
        """
        Return a synchronous function corresponding
        to an MCP tool.

        Arg:
            name (str): the name of the functin

        Return:
            Callable: The function
        """

        def tool_callable(**args: dict) -> Any:
            """
            Synchronous wrapper around an async MCP tool.

            Arg:
                **args: The args of the fonction

            Return:
                Any: The output of the fonction
            """

            if self.session is None:
                raise MCPClientError(
                    "Client not logged in"
                )
            if self.loop is None:
                raise MCPClientError(
                    "Uninitialized event loop"
                )

            future = asyncio.run_coroutine_threadsafe(
                self.session.call_tool(
                    name,
                    args or {},
                ),
                self.loop,
            )

            return future.result()

        return tool_callable

    def get_tools_callable(
        self,
        tools: list[Any],
    ) -> dict[str, Callable]:
        """
        Return a dictionary containing one callable
        for each MCP tool.

        Arg:
            tools (list): The mcp tools

        Return (dict[str, Callable]): a dict with
            str, the name of the function
            callable: the MCP tool
        """

        return {
            tool.name: self.make_callable(tool.name)
            for tool in tools
        }

    def close(self) -> None:
        """
        Close the MCP connection.
        """

        if self.loop is None:
            return

        if self._shutdown_event is not None:

            self.loop.call_soon_threadsafe(
                self._shutdown_event.set
            )

        if self.thread is not None:
            self.thread.join()

        self.thread = None
        self.loop = None
        self.session = None
        self.connected.clear()
        self.loop_ready.clear()
        self._shutdown_event = None


def test_agent() -> None:

    client = MCPClient(
        "http",
        server_url="http://127.0.0.3:8000/mcp",
        file_path="mcp_tools_swebench.py"
    )

    try:
        # Connexion
        client.connect()

        # Récupération des outils
        data = client.list_tools()

        print("============ TOOLS ============")

        for tool in data:
            print(tool.name)

        print("===============================\n")

        # Création des wrappers
        tools = client.get_tools_callable(data)

        # Code généré par le LLM
        code = """
result = get_patch()

print(result)
"""

        print("============ LLM CODE ==========")
        print(code)
        print("===============================\n")

        # Exécution du code LLM
        exec(code, tools)

    except (
        MCPClientError,
        MCPError,
        httpx.ConnectError,
    ) as e:
        print("Erreur :", e)

    finally:
        client.close()


if __name__ == "__main__":
    try:
        test_agent()
    except Exception as e:
        print("Erreur :", e)
