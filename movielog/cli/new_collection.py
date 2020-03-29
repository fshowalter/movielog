from prompt_toolkit.shortcuts import confirm

from movie_db import watchlist
from movie_db.cli import _ask


def prompt() -> None:
    name = _ask.prompt('Collection name: ')
    if name and confirm(f'{name}?'):
        watchlist.add_collection(name)
