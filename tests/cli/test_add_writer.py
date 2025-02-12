from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_writer
from movielog.repository.datasets.dataset_name import DatasetName
from movielog.repository.db import names_table
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_add_person_to_watchlist(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch("movielog.cli.add_director.repository_api.add_person_to_watchlist")


@pytest.fixture(autouse=True)
def seed_db() -> None:
    names_table.reload(
        [
            DatasetName(
                imdb_id="nm0762727",
                full_name="Jimmy Sangster",
                known_for_titles=["Horror of Dracula", "The Curse of Frankenstein"],
            ),
            DatasetName(
                imdb_id="nm0102824",
                full_name="Leigh Brackett",
                known_for_titles=[
                    "The Big Sleep",
                    "Rio Bravo",
                    "The Empire Strikes Back",
                ],
            ),
            DatasetName(
                imdb_id="nm0276169",
                full_name="Tom Holland",
                known_for_titles=["Fright Night", "Childs Play"],
            ),
        ]
    )


def test_calls_add_writer(mock_input: MockInput, mock_add_person_to_watchlist: MagicMock) -> None:
    mock_input(["Leigh Brackett", Enter, Down, Enter, "y", Enter])
    add_writer.prompt()

    mock_add_person_to_watchlist.assert_called_once_with(
        imdb_id="nm0102824", name="Leigh Brackett", watchlist="writers"
    )


def test_does_not_call_add_writer_if_no_selection(
    mock_input: MockInput, mock_add_person_to_watchlist: MagicMock
) -> None:
    mock_input([Escape, Enter])
    add_writer.prompt()

    mock_add_person_to_watchlist.assert_not_called()
