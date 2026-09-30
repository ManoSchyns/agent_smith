import argparse


def parse_args() -> argparse.Namespace:
    """
    Parses the arguments passed to the command line and retrieves them

    Return:
        An argparse object with the retrieved arguments
    """
    parser = argparse.ArgumentParser(
        description="SWEBENCH agent"
    )

    parser.add_argument(
        "--task-file",
        type=str,
        help="Path to the SWEBENCH task file"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Path to the output file"
    )

    parser.add_argument(
        "--model-name",
        type=str,
        help="The name of the model"
    )

    parser.add_argument(
        "--provider-url",
        type=str,
        help="Url to the Api of the LLM"
    )
    return parser.parse_args()


def analyse_args(parser: argparse.Namespace) -> bool:
    """
    Parses the arguments. Checks their validity.

    Arg:
        Object argparse with the arguments

    Return
        True / False if the arguments are valid
    """
    KEYS = [
        "task_file",
        "output",
        "model_name",
        "provider_url"
    ]

    args_dict: dict = vars(parser)
    try:
        for key in KEYS:
            if args_dict[key] is None:
                return False
    except KeyError:
        return False
    return True


if __name__ == "__main__":
    parser = parse_args()
    if analyse_args(parser):
        print("Niceee")
    else:
        print("Baddd")
