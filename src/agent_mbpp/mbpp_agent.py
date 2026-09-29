from .model import MBPPError, MBPPTaskInput
from .parser import parse_args, analyse_args
from .utils import load_task_file, export_result, get_solution_output
import argparse
from src.orchestrators import orchestrateur
import time


def mbpp_agent() -> None:
    """
    Agent MBPP
    """
    start_time = time.time()
    parser: argparse.Namespace = parse_args()
    if not analyse_args(parser):
        print("The arguments entered are invalid.")
        return

    try:
        task: MBPPTaskInput = load_task_file(parser.task_file)

        prompt_task: str = (task.task_definition + " " +
                            task.function_definition)

        ret_val: dict = orchestrateur(
            type="MBPP",
            prompt=prompt_task,
            model_name=parser.model_name,
            provider_url=parser.provider_url)

        export_result(parser.output,
                      get_solution_output(ret_val, start_time, task))

    except MBPPError as e:
        print(e)
        return
