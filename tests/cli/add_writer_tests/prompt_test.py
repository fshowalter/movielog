from typing import Callable, List
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_writer
from tests.cli.keys import Down, Enter, Escape
from tests.cli.typehints import CreditTuple, PosixPipeInput


@pytest.fixture(autouse=True)
def mock_watchlist_add_writer(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.add_writer.watchlist.add_writer")


@pytest.fixture(autouse=True)
def seed_db(seed_people: Callable[[List[CreditTuple]], None]) -> None:
    seed_people(
        [
            (
                "nm0762727",
                "Jimmy Sangster",
                [
                    ("tt0051554", "Horror of Dracula", 1958, []),
                    ("tt0050280", "The Curse of Frankenstein", 1957, []),
                ],
            ),
            ("nm0102824", "Leigh Brackett", [("tt0053221", "Rio Bravo", 1959, [])]),
            ("nm0276169", "Tom Holland", [("tt0089175", "Fright Night", 1985, [])]),
        ]
    )


def test_calls_add_director(
    mock_input: PosixPipeInput, mock_watchlist_add_writer: MagicMock
) -> None:
    mock_input.send_text(f"Leigh Brackett{Enter}{Down}{Enter}y{Enter}")  # noqa: WPS221
    add_writer.prompt()

    mock_watchlist_add_writer.assert_called_once_with(
        imdb_id="nm0102824",
        name="Leigh Brackett",
    )


def test_does_not_call_add_director_if_no_selection(
    mock_input: PosixPipeInput, mock_watchlist_add_writer: MagicMock
) -> None:
    mock_input.send_text(f"{Escape}{Enter}")  # noqa: WPS221
    add_writer.prompt()

    mock_watchlist_add_writer.assert_not_called()
