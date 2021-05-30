from movielog import api as movielog_api
from movielog.cli import ask, confirm


def prompt() -> None:
    name = ask.prompt("Collection name: ")
    if name and confirm.prompt(f"<cyan>{name}</cyan>?"):
        movielog_api.add_collection(name)
