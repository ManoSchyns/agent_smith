from .model import MBPPError, MBPPTaskInput
from .parser import parse_args, analyse_args
from .utils import load_task_file, export_result
import argparse
from src.orchestrator import orchestrateur


def mbpp_agent() -> None:
    parser: argparse.Namespace = parse_args()
    if not analyse_args(parser):
        print("Les arguments rentres sont invalides")
        return

    try:
        task: MBPPTaskInput = load_task_file(parser.task_file)
        prompt_task: str = task.task_definition + " " + task.function_definition
        print(orchestrateur(prompt=prompt_task,
                            model_name=parser.model_name,
                            provider_url=parser.provider_url))
    except MBPPError as e:
        print(e)
        return

    