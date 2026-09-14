from typing import Any, Callable
from contextlib import AsyncExitStack
import httpx
import asyncio
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
    The MCP client. For connections to servers via STDIO or HTTP

    Arguments:
        transport(str): STDIO or HTTP. How to connect to the server
        file_path(str) | None: The path to the file for STDIO
        server_url(str): The URL of the HTTP server
    """

    def __init__(
        self,
        transport: str,
        file_path: str | None = None,
        server_url: str | None = None,
    ):
        self.transport = transport

        self.server_command = "python"

        if file_path:
            self.file_path = [file_path]
        else:
            self.file_path = []

        self.server_url = server_url

        self.session: ClientSession | None = None

        self._exit_stack = AsyncExitStack()

    async def connect(self) -> None:
        """
        Initialize the server connection
        """

        if self.session is not None:
            return

        if self.transport == "stdio":
            await self.stdio_connect()

        elif self.transport == "http":
            await self.http_connect()

        else:
            raise MCPClientError(
                f"Transport inconnu : {self.transport}"
            )
        if self.session:
            await self.session.initialize()

    async def stdio_connect(self) -> None:
        """
        Initialize the server connection in STDIO
        """

        server_params = StdioServerParameters(
            command=self.server_command,
            args=self.file_path,
        )

        read, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )

    async def http_connect(self) -> None:
        """
        Initialize the server connection in HTTP
        """

        if self.server_url is None:
            raise MCPClientError(
                "server_url est requis pour HTTP"
            )

        read, write, *_ = await self._exit_stack.enter_async_context(
            streamable_http_client(self.server_url)
        )

        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )

    async def list_tools(self) -> Any:
        """
        List the tools provided by the server

        Return (Any): Tools
        """

        if self.session is None:
            raise MCPClientError("Client non connecté")

        result: Any = await self.session.list_tools()

        return result.tools

    def make_callable(self, name: str) -> Callable:
        """
        Returns a function corresponding to the tool's name

        Arg:
            name (str): The function name

        Return:
            (Callable): The function to call the server for this name
        """

        async def tool_callable(**args: dict) -> Any:
            """
            Call the server to call the `name` function for `args`.

            Args:
                args(dict): The arguments
            Return:
                The server's response
            """

            if self.session is None:
                raise MCPClientError(
                    "Client non connecté"
                )

            return await self.session.call_tool(
                name,
                args or {},
            )

        return tool_callable

    def get_tools_callable(
        self,
        tools: list[Any],
    ) -> dict[str, Callable]:
        """
        For a list of tools, return the callables to launch these tools.

        Arg:
            tools: The list of tools

        Return:
            Dict[str, Callable]: For each tool, its corresponding function
        """

        return {
            tool.name: self.make_callable(tool.name)
            for tool in tools
        }

    async def close(self) -> None:
        """
        Close the current connection by removing it from the stack
        """

        await self._exit_stack.aclose()

        self.session = None


if __name__ == "__main__":

    async def test_agent() -> None:

        """client = MCPClient(
            "stdio",
            file_path="mcp_tools_mbpp.py"
        )"""
        client = MCPClient(
            "http",
            server_url="http://127.0.0.2:8000/mcp"
        )
        try:
            # Connection
            await client.connect()
            # Recuperation des outils
            data = await client.list_tools()

            # Transforme en callable
            tools = client.get_tools_callable(data)
            # On appelle ceux correspondant

            code = """
def tuple_to_int(nums):
    to_return = ""
    for num in nums:
        to_return += str(num)
    return to_return
"""
            test_list = [
                "assert tuple_to_int((4,5,6))==456",
                "assert tuple_to_int((5,6,7))==567"]

            print(tools)
            result = await tools["run_tests"](code=code, test_list=test_list)
            print(result)

        except (MCPClientError, MCPError, httpx.ConnectError) as e:
            print("Erreur lors de la connection :", e)
        finally:
            await client.close()
    try:
        asyncio.run(test_agent())
    except Exception as e:
        print(e)
