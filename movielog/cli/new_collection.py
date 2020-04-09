from movielog import watchlist
from movielog.cli import ask, confirm


def prompt() -> None:
    name = ask.prompt("Collection name: ")
    if name and confirm.prompt(f"<cyan>{name}</cyan>?"):
        watchlist.add_collection(name)
