import itertools
from typing import Literal

from tests.cli.keys import Down, Enter

ConfirmType = Literal["y", "n"]


def enter_text(text: str | None, confirm: ConfirmType | None = None) -> list[str]:
    input_stream = [Enter]

    if text:
        input_stream.insert(0, text)

    if confirm:
        input_stream.append(confirm)

    return input_stream


def select_option(option_number: int, confirm: Literal[ConfirmType] | None = None) -> list[str]:
    input_stream = []

    if option_number > 1:
        input_stream = [Down for _ in itertools.repeat(None, option_number - 1)]

    input_stream.append(Enter)

    if confirm:
        input_stream.append(confirm)

    return input_stream
