from typing import Sequence, Tuple

import pytest
from prompt_toolkit.formatted_text import AnyFormattedText
from pytest_mock import MockFixture

from movielog.cli import radio_list
from tests.cli.keys import Down, End, Enter, Home, Up
from tests.cli.typehints import PosixPipeInput

Options = Sequence[Tuple[int, AnyFormattedText]]


@pytest.fixture
def options(mocker: MockFixture) -> Options:
    return [
        (1, "option 1"),
        (2, "option 2"),
        (3, "option 3"),
        (4, "option 4"),
    ]


def test_can_use_down_to_wrap_to_top(
    mock_input: PosixPipeInput, options: Options
) -> None:
    mock_input.send_text(f"{Up}{Down}{Enter}")

    assert radio_list.prompt("Test", options) == 1


def test_can_use_end_to_jump_to_bottom(
    mock_input: PosixPipeInput, options: Options
) -> None:
    mock_input.send_text(f"{End}{Enter}")

    assert radio_list.prompt("Test", options) == 4


def test_can_use_home_to_jump_to_top(
    mock_input: PosixPipeInput, options: Options
) -> None:
    mock_input.send_text(f"{End}{Home}{Enter}")

    assert radio_list.prompt("Test", options) == 1
