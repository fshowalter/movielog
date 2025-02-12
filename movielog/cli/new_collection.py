from movielog.cli import ask, confirm
from movielog.repository import api as repository_api


def prompt() -> None:
    name = ask.prompt("Collection name: ")
    if name and confirm.prompt(f"<cyan>{name}</cyan>?"):
        repository_api.new_collection(name)
