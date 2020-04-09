from typing import Callable, List

import pytest
from pytest_mock import MockFixture

from movielog.cli import add_director
from tests.cli.keys import Down, Enter, Escape
from tests.cli.typehints import CreditTuple, PosixPipeInput


@pytest.fixture(autouse=True)
def mock_watchlist_add_director(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.add_director.watchlist.add_director")


@pytest.fixture(autouse=True)
def seed_db(seed_directors: Callable[[List[CreditTuple]], None]) -> None:
    seed_directors(
        [
            (
                "nm0279807",
                "Terence Fisher",
                [
                    ("tt0051554", "Horror of Dracula", 1958, []),
                    ("tt0050280", "The Curse of Frankenstein", 1957, []),
                ],
            ),
            ("nm0001328", "Howard Hawks", [("tt0053221", "Rio Bravo", 1959, [])]),
            ("nm0276169", "Tom Holland", [("tt0089175", "Fright Night", 1985, [])]),
        ]
    )


def test_calls_add_director(
    mock_input: PosixPipeInput, mock_watchlist_add_director: MockFixture
) -> None:
    mock_input.send_text(f"Howard Hawks{Enter}{Down}{Enter}y{Enter}")  # noqa: WPS221
    add_director.prompt()

    mock_watchlist_add_director.assert_called_once_with(
        imdb_id="nm0001328", name="Howard Hawks",
    )


def test_does_not_call_add_director_if_no_selection(
    mock_input: PosixPipeInput, mock_watchlist_add_director: MockFixture
) -> None:
    mock_input.send_text(f"{Escape}{Enter}")  # noqa: WPS221
    add_director.prompt()

    mock_watchlist_add_director.assert_not_called()
