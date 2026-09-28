from .model import MBPPError, MBPPTaskInput
from .parser import parse_args, analyse_args
from .utils import load_task_file, export_result, get_solution_output
import argparse
from src.orchestrator import orchestrateur, SolutionOutput,StepMetrics
import time


def mbpp_agent() -> None:
    start = time.time()
    parser: argparse.Namespace = parse_args()
    if not analyse_args(parser):
        print("Les arguments rentres sont invalides")
        return

    try:
        print("1")
        task: MBPPTaskInput = load_task_file(parser.task_file)
        prompt_task: str = task.task_definition + " " + task.function_definition
        ret_val: tuple[str, list[StepMetrics]] = orchestrateur(prompt=prompt_task,
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

    