from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_performer
from movielog.repository.imdb_http_person import PersonPage
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_add_person_to_watchlist(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch("movielog.cli.add_director.repository_api.add_person_to_watchlist")


@pytest.fixture(autouse=True)
def mock_search_person(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "movielog.cli.person_searcher.repository_api.get_person_page",
        return_value=PersonPage(
            imdb_id="nm0000078",
            name="John Wayne",
            known_for_titles=["Rio Bravo", "The Searchers", "Stagecoach"],
        ),
    )


def test_calls_add_performer(
    mock_input: MockInput, mock_add_person_to_watchlist: MagicMock
) -> None:
    mock_input(["a-test-aws-token", Enter, "nm0000078", Enter, Down, Enter, "y", Enter])
    add_performer.prompt()

    mock_add_person_to_watchlist.assert_called_once_with(
        imdb_id="nm0000078", name="John Wayne", watchlist="performers"
    )


def test_can_confirm_selection(
    mock_input: MockInput, mock_add_person_to_watchlist: MagicMock
) -> None:
    mock_input(
        [
            "a-test-aws-token",
            Enter,
            "nm0000078",
            Enter,
            Down,
            Enter,
            "n",
            "nm0000078",
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
