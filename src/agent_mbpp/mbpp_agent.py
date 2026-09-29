from .model import MBPPError, MBPPTaskInput
from .parser import parse_args, analyse_args
from .utils import load_task_file, export_result, get_solution_output
import argparse
from src.orchestrators import orchestrateur, StepMetrics
import time


def mbpp_agent() -> None:
    """
    Agent MBPP
    """
    start = time.time()
    parser: argparse.Namespace = parse_args()
    if not analyse_args(parser):
        print("The arguments entered are invalid.")
        return

    try:
        task: MBPPTaskInput = load_task_file(parser.task_file)

        prompt_task: str = (task.task_definition + " " +
                            task.function_definition)

        ret_val: tuple[str, str, list[StepMetrics]] = orchestrateur(
            type="MBPP",
            prompt=prompt_task,
            model_name=parser.model_name,
            provider_url=parser.provider_url)

        export_result(parser.output,
                      get_solution_output(
                          output=ret_val[1],
                          steps=ret_val[2],
                          task=task,
                          start_time=start,
                          system_prompt=ret_val[0]
                        ))

    except MBPPError as e:
        print(e)
        return
