from typing import Any, Callable

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
        file_path: list[str] | None = None,
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

        self._transport_context = None
        self._session_context = None

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

        self.session = await self._session_context.__aenter__()

        await self.session.initialize()


    async def stdio_connect(self) -> None:
        if self.server_command is None:
            raise MCPClientError("server_command est requis pour stdio")

        server_params = StdioServerParameters(
            command=self.server_command,
            args=self.file_path,
        )

        self._transport_context = stdio_client(server_params)

        read, write = await self._transport_context.__aenter__()

        self._session_context = ClientSession(read, write)


    async def http_connect(self) -> None:
        if self.server_url is None:
            raise MCPClientError("server_url est requis pour HTTP")

        self._transport_context = streamable_http_client(
            self.server_url
        )
        
        read, write = await self._transport_context.__aenter__()

        self._session_context = ClientSession(read, write)


    async def list_tools(self) -> list[Any]:
        if self.session is None:
            raise MCPClientError("Client non connecté")

        result = await self.session.list_tools()

        return result.tools
    

    async def get_tools_callable(self, tools: list[Any]) -> dict[str, Callable]:
        result: dict[str, Callable] = {}
        
        for tool in tools:
            result[tool.name] = await self.make_callable(tool.name)
        
        return result
    
    async def make_callable(self, name) -> Callable:

        async def tool_callable(**args) -> Any:
            if self.session is None:
                raise MCPClientError("Client non connecté")
            
            return await self.session.call_tool(
                name,
                args or {},
            )
        return tool_callable

    async def close(self) -> None:
        if self._session_context is not None:
            await self._session_context.__aexit__(
                None,
                None,
                None,
            )

        if self._transport_context is not None:
            await self._transport_context.__aexit__(
                None,
                None,
                None,
            )

        self.session = None
        self._session_context = None
        self._transport_context = None

if __name__ == "__main__":
    async def test():

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
            tools = await client.get_tools_callable(data)
            # On appelle ceux correspondant
            await tools["hello_world"]()

        except (MCPClientError, MCPError) as e:
            print("Erreur lors de la connection :",e)
        finally:
            await client.close()
    try:
        asyncio.run(test())
    except (CancelledError) as e:
        print("")
    except Exception:
        print("")