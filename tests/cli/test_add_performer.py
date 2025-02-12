from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_performer
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
                imdb_id="nm0001088",
                full_name="Peter Cushing",
                known_for_titles=["The Curse of Frankenstein", "Star Wars"],
            ),
            DatasetName(
                imdb_id="nm0000078",
                full_name="John Wayne",
                known_for_titles=["The Searchers", "Rio Bravo", "Stagecoach"],
            ),
            DatasetName(
                imdb_id="nm0000489",
                full_name="Christopher Lee",
                known_for_titles=[
                    "Horror of Dracula",
                    "The Mummy",
                    "The Lord of the Rings",
                ],
            ),
        ]
    )


def test_calls_add_performer(
    mock_input: MockInput, mock_add_person_to_watchlist: MagicMock
) -> None:
    mock_input(["John Wayne", Enter, Down, Enter, "y", Enter])
    add_performer.prompt()

    mock_add_person_to_watchlist.assert_called_once_with(
        imdb_id="nm0000078", name="John Wayne", watchlist="performers"
    )


def test_can_confirm_selection(
    mock_input: MockInput, mock_add_person_to_watchlist: MagicMock
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

    mock_add_person_to_watchlist.assert_called_once_with(
        imdb_id="nm0000078", name="John Wayne", watchlist="performers"
    )


def test_does_not_call_add_performer_if_no_selection(
    mock_input: MockInput, mock_add_person_to_watchlist: MagicMock
) -> None:
    mock_input([Escape, Enter])
    add_performer.prompt()

    mock_add_person_to_watchlist.assert_not_called()
