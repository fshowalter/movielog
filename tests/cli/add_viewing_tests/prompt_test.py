from datetime import date
from typing import Callable, List

import pytest
from pytest_mock import MockFixture

from movielog import movies, people
from movielog.cli import add_viewing
from tests.cli.keys import Backspace, Down, Enter, Escape
from tests.cli.typehints import MovieTuple, PosixPipeInput

Movie = movies.Movie
Person = people.Person
Principal = movies.Principal


@pytest.fixture(autouse=True)
def mock_viewings_add(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.add_viewing.viewings.add")


@pytest.fixture(autouse=True)
def stub_venues(mocker: MockFixture) -> MockFixture:
    venues = [
        "AFI Silver",
        "Alamo Drafthouse",
        "Blu-ray",
    ]

    return mocker.patch("movielog.cli.add_viewing.viewings.venues", return_value=venues)


@pytest.fixture(autouse=True)
def seed_db(seed_movies: Callable[[List[MovieTuple]], None]) -> None:
    seed_movies(
        [
            ("tt0051554", "Horror of Dracula", 1958, [("nm0001088", "Peter Cushing")]),
            (
                "tt0053221",
                "Rio Bravo",
                1959,
                [
                    ("nm0000078", "John Wayne"),
                    ("nm0001509", "Dean Martin"),
                    ("nm0625699", "Ricky Nelson"),
                ],
            ),
            (
                "tt0050280",
                "The Curse of Frankenstein",
                1957,
                [("nm0001088", "Peter Cushing")],
            ),
            ("tt0089175", "Fright Night", 1985, [("nm0001697", "Chris Sarandon")]),
            ("tt0116671", "Jack Frost", 1997, [("nm0531924", "Scott MacDonald")]),
        ]
    )


def test_calls_add_viewing(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(
        f"Rio Bravo{Enter}{Down}{Enter}y2016-03-12{Enter}y{Down}{Down}{Enter}y"  # noqa: WPS221
    )
    add_viewing.prompt()

    mock_viewings_add.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        viewing_date=date(2016, 3, 12),
        year=1959,
    )


def test_does_not_call_add_viewing_if_movie_is_none(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(f"{Escape}")  # noqa: WPS221
    add_viewing.prompt()

    mock_viewings_add.assert_not_called()


def test_does_not_call_add_viewing_if_date_is_none(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(
        f"Rio Bravo{Enter}{Down}{Enter}y{Escape}{Escape}"
    )  # noqa: WPS221
    add_viewing.prompt()

    mock_viewings_add.assert_not_called()


def test_guards_against_bad_dates(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(
        f"Rio Bravo{Enter}{Down}{Enter}y2016-3-32{Enter}{Backspace}1{Enter}y{Down}{Down}{Enter}y"  # noqa: E501, WPS221
    )
    add_viewing.prompt()

    mock_viewings_add.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        viewing_date=date(2016, 3, 31),
        year=1959,
    )
