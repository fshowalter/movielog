from prompt_toolkit.shortcuts import confirm

from movielog import watchlist_collection
from movielog.cli import ask


def prompt() -> None:
    name = ask.prompt("Collection name: ")
    if name and confirm(f"{name}?"):
        watchlist_collection.add(name)
