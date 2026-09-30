from .parser import parse_args, analyse_args
from .model import SWEBenchTaskInput, SWEBENCHError
from .utils import load_task_file, export_result, get_solution_output, export_scipt, start_docker, stop_docker
from src.orchestrators import orchestrateur

import argparse
import time
import os

def swebench_agent() -> None:
    """
    Agent MBPP
    """
    start_time = time.perf_counter()

    parser: argparse.Namespace = parse_args()
    if not analyse_args(parser):
        print("The arguments entered are invalid.")
        return

    try:
        task: SWEBenchTaskInput = load_task_file(parser.task_file)

        container = start_docker(task.docker_image)
        export_scipt(task.eval_script, container)

        prompt_task: str = (task.problem_statement + " " +
                                task.hints_text)
    
        ret_val: dict = orchestrateur(
            type="swebench",
            prompt=prompt_task,
            model_name=parser.model_name,
            provider_url=parser.provider_url)
    
        export_result(parser.output,
                      get_solution_output(ret_val, start_time, task))
    except KeyError as e:
        print("Impossible de travailler sans connaitre l'encvironnement du docker")
        return
    except SWEBENCHError as e:
        print(e)
        return
    finally:
        stop_docker(container)