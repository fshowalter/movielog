from typing import Sequence, Tuple

import pytest
from prompt_toolkit.formatted_text import AnyFormattedText
from pytest_mock import MockerFixture

from movielog.cli import radio_list
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, End, Enter, Home, Up

Options = Sequence[Tuple[int, AnyFormattedText]]


@pytest.fixture
def options(mocker: MockerFixture) -> Options:
    return [
        (1, "option 1"),
        (2, "option 2"),
        (3, "option 3"),
        (4, "option 4"),
    ]


def test_can_use_down_to_wrap_to_top(mock_input: MockInput, options: Options) -> None:
    mock_input([Up, Down, Enter])

    assert radio_list.prompt("Test", options) == 1


def test_can_use_end_to_jump_to_bottom(mock_input: MockInput, options: Options) -> None:
    mock_input([End, Enter])

    assert radio_list.prompt("Test", options) == 4


def test_can_use_home_to_jump_to_top(mock_input: MockInput, options: Options) -> None:
    mock_input([End, Home, Enter])

    assert radio_list.prompt("Test", options) == 1
