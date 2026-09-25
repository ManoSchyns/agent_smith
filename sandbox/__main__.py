import argparse
from sandbox_def import Sandbox


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sandbox for executing Python code."
    )

    parser.add_argument(
        "config",
        type=str,
        nargs="?",
        default=None,
        help="Path to the sandbox configuration file"
    )

    parser.add_argument(
        "--mcp-stdio",
        type=str,
        help="Path to the mcp sever"
    )

    parser.add_argument(
        "--mcp-server",
        type=str,
        help="Url to connect to the mcp server"
    )
    return parser.parse_args()


if __name__ == "__main__":
    parser = parse_args()
    connection_mcp: str | None = None

    if parser.mcp_server:
        connection_mcp = "http"
    elif parser.mcp_stdio:
        connection_mcp = "stdio"

    sandbox = Sandbox(config=parser.config,
                      connection_mcp=connection_mcp,
                      url_connection=parser.mcp_server,
                      file_path=parser.mcp_stdio)
    try:
        sandbox.deploy()
    finally:
        sandbox.close()
