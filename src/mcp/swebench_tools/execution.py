import subprocess
import json
from pathlib import Path
import os


def run_tests_tool() -> str:
    """
    Execute the evaulation script

    Return:
        A JSON object with the result if successed or not
    """
    EVAL_SCRIPT = "../../../script.sh"
    SCIPT_PATH = Path(__file__).parent/EVAL_SCRIPT

    result = subprocess.run(
        ["bash", str(SCIPT_PATH)],
        capture_output=True,
        text=True
    )
    return json.dumps({
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    })


def get_patch_tool() -> str:
    """
    Retrieve the unified git diff of all changes made to the repository

    Return:
        A JSON object with the result if successed or not and the git diffs
    """
    try:
        DIRECTORY = os.environ["TESTBED_PATH"]
    except KeyError:
        return json.dumps({
            "success": False,
            "output": "Unable to find the folder to do the get patch"
        })
    result = subprocess.run(
        ["git", "-c", "core.fileMode=false", "diff"],
        cwd=DIRECTORY,
        capture_output=True,
        text=True
    )

    return json.dumps({
        "success": True,
        "output": result.stdout
    })


def run_command_tool(command: str, workdir: str) -> str:
    """
    Execute a shell command in the specified working directory

    Args:
        command (str): the command to execute
        workdir (str): the folder in which to execute the command

    Return:
        Returns the command’s stdout, stderr, and exit code
    """
    result = subprocess.run(
        command,
        cwd=workdir,
        shell=True,
        capture_output=True,
        text=True
    )
    return json.dumps({
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        })


if __name__ == "__main__":
    print(run_command_tool('ls -l', "src/mcp/mcp_client"))
