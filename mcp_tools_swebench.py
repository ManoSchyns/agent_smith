from mcp.server.mcpserver import MCPServer
from dotenv import load_dotenv
import sys
import os


load_dotenv()
DIRECTORY = os.environ["TESTBED_PATH"]

mcp = MCPServer("Agent Smith")

# @mcp.tool()


if __name__ == "__main__":
    """
    Si on le lance sans args -> stdio
    N importe quel args -> http
    """
    if len(sys.argv) > 1:
        mcp.run(transport="streamable-http",
                host="127.0.0.3")
    else:
        mcp.run(transport="stdio")
