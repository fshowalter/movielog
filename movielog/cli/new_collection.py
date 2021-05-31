from movielog import api as movielog_api
from movielog.cli import ask, confirm


def prompt() -> None:
    name = ask.prompt("Collection name: ")
    if name and confirm.prompt("<cyan>{0}</cyan>?".format(name)):
        movielog_api.add_collection(name)
