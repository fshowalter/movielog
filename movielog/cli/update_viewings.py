from prompt_toolkit.shortcuts import confirm

from movie_db import viewings


def prompt() -> None:
    if confirm('Reload Db viewings table?'):
        viewings.update()
