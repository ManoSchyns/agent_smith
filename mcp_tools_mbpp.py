from mcp.server.mcpserver import MCPServer
import sys


mcp = MCPServer("A")

@mcp.tool()
def hello_world() -> None:
    print("Hello World !")


if __name__ == "__main__":
    """
    Si on le lance sans args -> stdio
    N importe quel args -> http
    """
    if len(sys.argv) > 1:
        mcp.run(transport="streamable-http",
                host="127.0.0.2")
    else:
        mcp.run(transport="stdio")
