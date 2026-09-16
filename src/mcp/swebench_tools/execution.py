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


if __name__ == "__main__":
    print(run_tests_tool())
