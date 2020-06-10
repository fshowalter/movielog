from prompt_toolkit.shortcuts import confirm

from movielog import viewings


def prompt() -> None:
    if confirm("Reload viewings table?"):
        viewings.export()
