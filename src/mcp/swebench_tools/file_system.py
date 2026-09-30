import subprocess
import json
import os
import fnmatch


def get_container_id():
    try:
        return os.environ["SCIPT_PATH"]
    except KeyError:
        return None


def read_file_tool(filepath: str, start_line: int, end_line: int) -> str:
    """
    Reads a range of lines from a file inside the Docker container.

    Args:
        filepath (str): Path to the file inside the container.
        start_line (int): Zero-based index of the first line.
        end_line (int): Zero-based exclusive index of the last line.

    Return:
        A JSON object containing the result.
    """

    if start_line < 0 or end_line < 0:
        return json.dumps({
            "success": False,
            "output": "Error: start_line and end_line must be positive integers"
        })

    if start_line > end_line:
        return json.dumps({
            "success": False,
            "output": "Error: start_line must be lower than or equal to end_line"
        })

    container_id = get_container_id()

    if container_id is None:
        return json.dumps({
            "success": False,
            "output": "Unable to get the id of the docker"
        })

    # sed uses 1-based inclusive line numbers.
    first_line = start_line + 1
    last_line = end_line

    result = subprocess.run(
        [
            "docker",
            "exec",
            container_id,
            "bash",
            "-c",
            f"sed -n '{first_line},{last_line}p' '{filepath}'"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return json.dumps({
            "success": False,
            "output": result.stderr
        })

    lines = result.stdout.splitlines(keepends=True)

    output = ""

    for i, line in enumerate(lines):
        output += f"{start_line + i + 1} {line}"

    return json.dumps({
        "success": True,
        "output": output
    })


def edit_file_tool(filepath: str, old_str: str, new_str: str) -> str:
    """
    Edit a file inside the Docker container by replacing old_str with new_str.

    Args:
        filepath (str): Path to the file inside the container.
        old_str (str): Content to replace.
        new_str (str): Replacement content.

    Return:
        A JSON object containing the result.
    """

    container_id = get_container_id()

    if container_id is None:
        return json.dumps({
            "success": False,
            "output": "Unable to get the id of the docker"
        })

    # Read the file from the container.
    result = subprocess.run(
        [
            "docker",
            "exec",
            container_id,
            "cat",
            filepath
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return json.dumps({
            "success": False,
            "output": result.stderr
        })

    content = result.stdout

    if old_str not in content:
        return json.dumps({
            "success": False,
            "output": f"The content: {old_str}\nCould not be found"
        })

    new_content = content.replace(old_str, new_str)

    # Use stdin to send the modified content to the container.
    result = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            container_id,
            "bash",
            "-c",
            f"cat > '{filepath}'"
        ],
        input=new_content,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return json.dumps({
            "success": False,
            "output": result.stderr
        })

    return json.dumps({
        "success": True,
        "output": (
            f"The {filepath} file update has "
            "been successfully completed."
        )
    })


def list_files_tool(directory: str, pattern: str) -> str:
    """
    Lists files inside the Docker container that match a pattern.

    Args:
        directory (str): Directory inside the container.
        pattern (str): Filename pattern, for example "*.py".

    Return:
        A JSON object containing the matching files.
    """

    container_id = get_container_id()

    if container_id is None:
        return json.dumps({
            "success": False,
            "output": "Unable to get the id of the docker"
        })

    result = subprocess.run(
        [
            "docker",
            "exec",
            container_id,
            "find",
            directory,
            "-type",
            "f"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return json.dumps({
            "success": False,
            "output": result.stderr
        })

    all_files = []

    for filepath in result.stdout.splitlines():
        filename = filepath.rsplit("/", 1)[-1]

        if fnmatch.fnmatch(filename, pattern):
            all_files.append(filepath)

    return json.dumps({
        "success": True,
        "output": all_files
    })
