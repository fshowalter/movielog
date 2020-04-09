from typing import cast

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import confirm


def prompt(text: str) -> bool:
    return cast(bool, confirm(HTML("text")))
