from movielog.cli import ask, confirm
from movielog.repository import api as repository_api


def prompt() -> None:
    name = ask.prompt("Collection name: ")
    if name and confirm.prompt("<cyan>{0}</cyan>?".format(name)):
        repository_api.new_collection(name)
