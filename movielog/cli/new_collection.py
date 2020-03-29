from prompt_toolkit.shortcuts import confirm

from movielog import watchlist
from movielog.cli.internal import ask


def prompt() -> None:
    name = ask.prompt("Collection name: ")
    if name and confirm(f"{name}?"):
        watchlist.add_collection(name)
