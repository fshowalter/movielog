from prompt_toolkit.shortcuts import confirm

from movielog import viewings


def prompt() -> None:
    if confirm("Reload Db viewings table?"):
        viewings.update()
