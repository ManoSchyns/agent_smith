from typing import Any, Callable
from contextlib import AsyncExitStack
import httpx
import asyncio
from asyncio import CancelledError

from mcp import ClientSession, StdioServerParameters, MCPError
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client


class MCPClientError(Exception):
    pass


class MCPClient:

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

        await self.session.initialize()

    async def stdio_connect(self) -> None:

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

    async def list_tools(self) -> list[Any]:

        if self.session is None:
            raise MCPClientError("Client non connecté")

        result = await self.session.list_tools()

        return result.tools

    def make_callable(self, name: str) -> Callable:

        async def tool_callable(**args) -> Any:

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

        return {
            tool.name: self.make_callable(tool.name)
            for tool in tools
        }

    async def close(self) -> None:

        await self._exit_stack.aclose()

        self.session = None

if __name__ == "__main__":
    async def test_agent():

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
            result = await tools["hello_world"]()
            print(result)

        except (MCPClientError, MCPError, httpx.ConnectError) as e:
            print("Erreur lors de la connection :",e)
        finally:
            await client.close()
    try:
        asyncio.run(test_agent())
    except Exception as e:
        print(e)