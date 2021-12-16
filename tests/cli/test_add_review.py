from datetime import date
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_review
from movielog.moviedata.core import movies_table, people_table
from tests.cli.conftest import MockInput
from tests.cli.keys import Backspace, Down, End, Enter, Escape


@pytest.fixture(autouse=True)
def mock_create_review(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.add_review.movielog_api.create_review")


@pytest.fixture(autouse=True)
def stub_venues(mocker: MockerFixture) -> None:
    venues = [
        "AFI Silver",
        "Alamo Drafthouse",
        "Blu-ray",
    ]

    mocker.patch(
        "movielog.cli.add_review.movielog_api.recent_venues", return_value=venues
    )


@pytest.fixture(autouse=True)
def seed_db() -> None:
    people_table.reload(
        [
            people_table.Row(
                imdb_id="nm0001088",
                full_name="Peter Cushing",
                known_for_title_ids="tt0051554,tt0050280",
            ),
            people_table.Row(
                imdb_id="nm0000078",
                full_name="John Wayne",
                known_for_title_ids="tt0053221",
            ),
            people_table.Row(
                imdb_id="nm0001509",
                full_name="Dean Martin",
                known_for_title_ids="tt0053221",
            ),
            people_table.Row(
                imdb_id="nm0625699",
                full_name="Ricky Nelson",
                known_for_title_ids="tt0053221",
            ),
        ]
    )

    movies_table.reload(
        [
            movies_table.Row(
                imdb_id="tt0051554",
                title="Horror of Dracula",
                original_title="Dracula",
                year=1958,
                runtime_minutes=None,
                principal_cast_ids="nm0001088",
                votes=23,
                imdb_rating=4.5,
            ),
            movies_table.Row(
                imdb_id="tt0053221",
                title="Rio Bravo",
                original_title=None,
                year=1959,
                runtime_minutes=None,
                principal_cast_ids="nm0000078,nm0001509,nm0625699",
                votes=32,
                imdb_rating=7.8,
            ),
            movies_table.Row(
                imdb_id="tt0050280",
                title="Curse of Frankenstein",
                original_title=None,
                year=1957,
                runtime_minutes=None,
                principal_cast_ids="nm0001088",
                votes=16,
                imdb_rating=5.8,
            ),
        ]
    )


CLEAR_DEFAULT_DATE = "".join(
    [
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
        Backspace,
    ]
)


def test_calls_add_review(mock_input: MockInput, mock_create_review: MagicMock) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-03-12",
            Enter,
            "y",
            Down,
            Down,
            Enter,
            "yA+",
            Enter,
            "y",
        ]
    )

    add_review.prompt()

    mock_create_review.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        year=1959,
        grade="A+",
        review_date=date(2016, 3, 12),
    )


def test_can_confirm_movie(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(
        [
            "Horror of Dracula",
            Enter,
            Down,
            Enter,
            "n",
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-03-12",
            Enter,
            "y",
            Down,
            Down,
            Enter,
            "yA+",
            Enter,
            "y",
        ]
    )
    add_review.prompt()

    mock_create_review.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        year=1959,
        grade="A+",
        review_date=date(2016, 3, 12),
    )


def test_does_not_call_add_review_if_no_movie(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input([Escape])
    add_review.prompt()

    mock_create_review.assert_not_called()


def test_does_not_call_add_review_if_no_date(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(["Rio Bravo", Enter, Down, Enter, "y", Escape, Escape])
    add_review.prompt()

    mock_create_review.assert_not_called()


def test_does_not_call_add_review_if_no_grade(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-03-12",
            Enter,
            "y",
            Down,
            Down,
            Enter,
            "y",
            Enter,
            Escape,
            Escape,
        ]
    )
    add_review.prompt()

    mock_create_review.assert_not_called()


def test_can_confirm_grade(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-03-12",
            Enter,
            "y",
            Down,
            Down,
            Enter,
            "yB+",
            Enter,
            "n",
            "A+",
            Enter,
            "y",
        ]
    )
    add_review.prompt()

    mock_create_review.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        review_date=date(2016, 3, 12),
        year=1959,
        grade="A+",
    )


def test_guards_against_bad_dates(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-3-32",
            Enter,
            Backspace,
            "1",
            Enter,
            "y",
            Down,
            Down,
            Enter,
            "yA+",
            Enter,
            "y",
        ]
    )
    add_review.prompt()

    mock_create_review.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        review_date=date(2016, 3, 31),
        year=1959,
        grade="A+",
    )


def test_can_confirm_date(mock_input: MockInput, mock_create_review: MagicMock) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-3-13",
            Enter,
            "n",
            CLEAR_DEFAULT_DATE,
            "2016-3-12",
            Enter,
            "y",
            Down,
            Down,
            Enter,
            "yA+",
            Enter,
            "y",
        ]
    )
    add_review.prompt()

    mock_create_review.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        year=1959,
        grade="A+",
        review_date=date(2016, 3, 12),
    )


def test_can_add_new_venue(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-03-12",
            Enter,
            "y",
            End,
            Enter,
            "4k UHD Blu-ray",
            Enter,
            "yA+",
            Enter,
            "y",
        ]
    )
    add_review.prompt()

    mock_create_review.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="4k UHD Blu-ray",
        year=1959,
        grade="A+",
        review_date=date(2016, 3, 12),
    )


def test_can_confirm_new_venue(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-03-12",
            Enter,
            "y",
            End,
            Enter,
            "2k UHD Blu-ray",
            Enter,
            "n",
            End,
            Enter,
            "4k UHD Blu-ray",
            Enter,
            "yA+",
            Enter,
            "y",
        ]
    )
    add_review.prompt()

    mock_create_review.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="4k UHD Blu-ray",
        year=1959,
        grade="A+",
        review_date=date(2016, 3, 12),
    )


def test_does_not_call_add_review_if_no_venue(
    mock_input: MockInput, mock_create_review: MagicMock
) -> None:
    mock_input(
        [
            "Rio Bravo",
            Enter,
            Down,
            Enter,
            "y",
            CLEAR_DEFAULT_DATE,
            "2016-03-12",
            Enter,
            "y",
            End,
            Enter,
            Escape,
            Escape,
        ]
    )
    add_review.prompt()

    mock_create_review.assert_not_called()
