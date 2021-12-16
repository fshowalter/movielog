from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_writer
from movielog.moviedata.core import movies_table, people_table
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_add_writer(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.add_writer.movielog_api.add_writer")


@pytest.fixture(autouse=True)
def seed_db() -> None:
    people_table.reload(
        [
            people_table.Row(
                imdb_id="nm0762727",
                full_name="Jimmy Sangster",
                known_for_title_ids="tt0051554,tt0050280",
            ),
            people_table.Row(
                imdb_id="nm0102824",
                full_name="Leigh Brackett",
                known_for_title_ids="tt0053221,tt0000000",
            ),
            people_table.Row(
                imdb_id="nm0276169",
                full_name="Tom Holland",
                known_for_title_ids="tt0089175",
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
                votes=32,
                imdb_rating=4.5,
            ),
            movies_table.Row(
                imdb_id="tt0053221",
                title="Rio Bravo",
                original_title="Rio Bravo",
                year=1959,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=23,
                imdb_rating=8.1,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=16,
                imdb_rating=4,
            ),
        ]
    )


def test_calls_add_writer(mock_input: MockInput, mock_add_writer: MagicMock) -> None:
    mock_input(["Leigh Brackett", Enter, Down, Enter, "y", Enter])
    add_writer.prompt()

    mock_add_writer.assert_called_once_with(
        imdb_id="nm0102824",
        name="Leigh Brackett",
    )


def test_does_not_call_add_writer_if_no_selection(
    mock_input: MockInput, mock_add_writer: MagicMock
) -> None:
    mock_input([Escape, Enter])
    add_writer.prompt()

    mock_add_writer.assert_not_called()
