from typing import Callable, List
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_performer
from tests.cli.keys import Down, Enter, Escape
from tests.cli.typehints import CreditTuple, PosixPipeInput


@pytest.fixture(autouse=True)
def mock_watchlist_add_performer(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch("movielog.cli.add_performer.watchlist.add_performer")


@pytest.fixture(autouse=True)
def seed_db(seed_performers: Callable[[List[CreditTuple]], None]) -> None:
    seed_performers(
        [
            (
                "nm0001088",
                "Peter Cushing",
                [("tt0051554", "Horror of Dracula", 1958, [])],
            ),
            ("nm0000078", "John Wayne", [("tt0053221", "Rio Bravo", 1959, [])]),
            ("nm0001697", "Chris Sarandon", [("tt0089175", "Fright Night", 1985, [])]),
        ]
    )


def test_calls_add_performer(
    mock_input: PosixPipeInput, mock_watchlist_add_performer: MagicMock
) -> None:
    mock_input.send_text(f"John Wayne{Enter}{Down}{Enter}y{Enter}")  # noqa: WPS221
    add_performer.prompt()

    mock_watchlist_add_performer.assert_called_once_with(
        imdb_id="nm0000078", name="John Wayne",
    )


def test_can_confirm_selection(
    mock_input: PosixPipeInput, mock_watchlist_add_performer: MagicMock
) -> None:
    mock_input.send_text(
        f"Chris Sarandon{Enter}{Down}{Enter}nJohn Wayne{Enter}{Down}{Enter}y{Enter}"  # noqa: WPS221
    )
    add_performer.prompt()

    mock_watchlist_add_performer.assert_called_once_with(
        imdb_id="nm0000078", name="John Wayne",
    )


def test_does_not_call_add_performer_if_no_selection(
    mock_input: PosixPipeInput, mock_watchlist_add_performer: MagicMock
) -> None:
    mock_input.send_text(f"{Escape}{Enter}")  # noqa: WPS221
    add_performer.prompt()

    mock_watchlist_add_performer.assert_not_called()
