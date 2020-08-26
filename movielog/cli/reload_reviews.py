from prompt_toolkit.shortcuts import confirm

from movielog import reviews


def prompt() -> None:
    if confirm("Reload reviews table?"):
        reviews.update()
