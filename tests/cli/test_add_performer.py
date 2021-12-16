from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_performer
from movielog.moviedata.core import movies_table, people_table
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_add_performer(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch("movielog.cli.add_performer.movielog_api.add_performer")


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
                imdb_id="nm0000489",
                full_name="Christopher Lee",
                known_for_title_ids="tt0051554,tt0050280",
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
                principal_cast_ids=None,
                votes=23,
                imdb_rating=4.5,
            ),
            movies_table.Row(
                imdb_id="tt0053221",
                title="Rio Bravo",
                original_title="Rio Bravo",
                year=1959,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=32,
                imdb_rating=7,
            ),
            movies_table.Row(
                imdb_id="tt0050280",
                title="Curse of Frankenstein",
                original_title="Curse of Frankenstein",
                year=1957,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=16,
                imdb_rating=6.2,
            ),
        ]
    )


def test_calls_add_performer(
    mock_input: MockInput, mock_add_performer: MagicMock
) -> None:
    mock_input(["John Wayne", Enter, Down, Enter, "y", Enter])
    add_performer.prompt()

    mock_add_performer.assert_called_once_with(
        imdb_id="nm0000078",
        name="John Wayne",
    )


def test_can_confirm_selection(
    mock_input: MockInput, mock_add_performer: MagicMock
) -> None:
    mock_input(
        [
            "Peter Cushing",
            Enter,
            Down,
            Enter,
            "n",
            "John Wayne",
            Enter,
            Down,
            Enter,
            "y",
            Enter,
        ]
    )
    add_performer.prompt()

    mock_add_performer.assert_called_once_with(
        imdb_id="nm0000078",
        name="John Wayne",
    )


def test_does_not_call_add_performer_if_no_selection(
    mock_input: MockInput, mock_add_performer: MagicMock
) -> None:
    mock_input([Escape, Enter])
    add_performer.prompt()

    mock_add_performer.assert_not_called()
