import argparse


def parse_args() -> argparse.Namespace:
    """
    Parse les arguments mis en ligne de commande et les recuperes

    Return:
        Un object argparse avec les arguments recuperes
    """
    parser = argparse.ArgumentParser(
        description="MBPP agent"
    )

    parser.add_argument(
        "--task-file",
        type=str,
        help="Path to the MBPP task file"
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
    Analyse les arguments parse. Verifie leurs validite

    Arg:
        Object argparse avec les args

    Return
        True / False si les arguments sont valides
    """
    KEYS=[
        "task_file",
        "output",
        "model_name",
        "provider_url"
    ]

    args_dict: dict = vars(parser)
    try:
        for key in KEYS:
            if args_dict[key] == None:
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
