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

    try:
        ID = os.environ["SCIPT_PATH"]
    except KeyError:
        return json.dumps({
            "success": False,
            "output": "Unable to get the id of the docker"
        })

    result = subprocess.run(
        ["docker", "exec", ID, "bash", "script.sh"],
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
        ID = os.environ["SCIPT_PATH"]
    except KeyError:
        return json.dumps({
            "success": False,
            "output": "Unable to get the id of the docker"
        })
    result = subprocess.run(
        ["docker", "exec", ID, "git", "-c", "core.fileMode=false", "diff"],
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
    try:
        ID = os.environ["SCIPT_PATH"]
    except KeyError:
        return json.dumps({
            "success": False,
            "output": "Unable to get the id of the docker"
        })

   

    result = subprocess.run(
        ["docker", "exec", "-w", workdir, ID, command],
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
