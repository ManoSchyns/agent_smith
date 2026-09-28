import json
from .model import MBPPTaskInput, MBPPError
from pydantic import ValidationError


def load_task_file(task_file: str) -> MBPPTaskInput:
    """
    Charge le fichier de tache

    Arg:
        task_file (str): le fichier de tache a charger

    Return:
        MBPPTaskInput: Le fichier pret a l emploi
    """
    try:
        with open(task_file, "r") as file:
            content = file.read()
            datas = json.loads(content)
            return MBPPTaskInput(**datas)
    except (FileNotFoundError, PermissionError,
            OSError, UnicodeDecodeError,
            json.decoder.JSONDecodeError,
            ValidationError) as e:
        raise MBPPError(f"Erreur lors de la recuperation du fichier des taches {e}")


def export_result():
    """
    Export le resultat du model
    TODO
    """
    pass

if __name__ == "__main__":
    try:
        print(load_task_file("mbpp_taskkkkk.json"))
    except MBPPError as e:
        print(e)