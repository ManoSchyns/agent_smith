import json
from .model import SWEBenchTaskInput, SWEBENCHError
from pydantic import ValidationError
from src.orchestrators import SolutionOutput, StepMetrics
import time
import subprocess
from pathlib import Path
import docker
import os


def load_task_file(task_file: str) -> SWEBenchTaskInput:
    """
    Loads the task file

    Arg:
        task_file(str): the task file to load

    Return:
        SWEBenchTaskInput: The ready-to-use file
    """
    try:
        with open(task_file, "r") as file:
            content = file.read()
            datas = json.loads(content)
            return SWEBenchTaskInput(**datas)
    except (FileNotFoundError, PermissionError,
            OSError, UnicodeDecodeError,
            json.decoder.JSONDecodeError,
            ValidationError) as e:
        raise SWEBENCHError(f"Error retrieving task file {e}")


def export_result(file_path: str, solution: SolutionOutput) -> None:
    """
    Export the model's output

    Args:
        file_path (str): the export file
        solution (SolutionOutput): The model's solution
    """
    try:
        with open(file_path, "w") as file:
            json.dump(solution.model_dump(),
                      file,
                      indent=4)
    except (FileNotFoundError, PermissionError,
            json.JSONDecodeError, OSError) as e:
        print(f"Export of result impossible: {e}")


def get_solution_output(orchest_output: dict,
                        start_time: float,
                        task: SWEBenchTaskInput) -> SolutionOutput:
    """
    Return the object SolutionOutput
    """
    is_error: bool = orchest_output["SUCCESS"]
    error: str | None = None
    if not is_error:
        error = orchest_output["OUTPUT"]

    steps: list[StepMetrics] = orchest_output["STEPS"]
    iterations: int = len(steps)
    total_requests: int = iterations
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_time_seconds: float = time.perf_counter() - start_time

    for step in steps:
        total_requests += step.retries
        total_input_tokens += step.input_tokens
        total_output_tokens += step.output_tokens

    return SolutionOutput(
        task_id=str(task.instance_id),
        benchmark="MBPP",
        success=is_error,
        solution=orchest_output["OUTPUT"],
        iterations=iterations,
        total_requests=total_requests,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        total_time_seconds=total_time_seconds,
        steps=steps,
        system_prompt=orchest_output["PROMPT"],
        error=error
    )


def export_scipt(script: str, container) -> None:
    """
    Export the script to its file

    Arg:
        script (str): the script
    """
    EVAL_SCRIPT = "../../script.sh"
    SCIPT_PATH = Path(__file__).parent/EVAL_SCRIPT

    try:
        with open(SCIPT_PATH, "w") as file:
            file.write(script)

        subprocess.run(
            ["chmod","u+x", SCIPT_PATH.absolute()]
            )
        print(container.id)
        subprocess.run(
            ["docker", "cp", SCIPT_PATH.absolute(), f"{container.id}:."]   
        )
        print(container.id)

    except (FileExistsError, FileNotFoundError,
            UnicodeDecodeError,
            OSError, PermissionError) as e:
        raise SWEBENCHError(f"The script could not be exported. {e}")


def start_docker(image: str) -> None:
    client = docker.from_env()

    container = client.containers.run(
        image,
        command="sleep infinity",
        detach=True
    )

    container.exec_run(
        ["python", "-m", "pip", "install", "pytest"]
    )
    os.environ["CONTAINER_ID"] = container.id

    return container

def stop_docker(container) -> None:
    container.stop()
    container.remove(force=True)


if __name__ == "__main__":
    try:
        print(load_task_file("mbpp_taskkkkk.json"))
    except SWEBENCHError as e:
        print(e)