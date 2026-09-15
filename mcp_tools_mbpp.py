from mcp.server.mcpserver import MCPServer
import sys
import json


mcp = MCPServer("Agent Smith")


@mcp.tool()
def run_tests(code: str, test_list: list[str]) -> str:
    """
    Runs the tests from the test list on the given code.

    Args:
        code(str): the code to execute
        test_list(list[str]): the tests to run

    Return:
        A JSON object with the result if successed or not
    """
    try:
        namespace: dict = {}
        exec(code, namespace)

        for test in test_list:
            exec(test, namespace)

        return json.dumps({
            "success": True,
            "output": "All test passed !"
        })

    except AssertionError as e:
        return json.dumps({
            "success": False,
            "output": f"AssertionError for the test : {test}: {e}"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "output": f"{e}"
        })


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
