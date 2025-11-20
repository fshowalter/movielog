from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_director
from movielog.repository.imdb_http_person import PersonPage
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_add_person_to_watchlist(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch("movielog.cli.add_director.repository_api.add_person_to_watchlist")


@pytest.fixture(autouse=True)
def mock_search_person(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "movielog.cli.person_searcher.imdb_http_person.get_person_page",
        return_value=PersonPage(
            imdb_id="nm0001328",
            name="Howard Hawks",
            known_for_titles=["Scarface", "Rio Bravo", "Only Angels Have Wings"],
        ),
    )


def test_calls_add_director(mock_input: MockInput, mock_add_person_to_watchlist: MagicMock) -> None:
    mock_input(["nm0001328", Enter, Down, Enter, "y", Enter])
    add_director.prompt()

    mock_add_person_to_watchlist.assert_called_once_with(
        watchlist="directors",
        imdb_id="nm0001328",
        name="Howard Hawks",
    )


def test_does_not_call_add_director_if_no_selection(
    mock_input: MockInput, mock_add_person_to_watchlist: MagicMock
) -> None:
    mock_input([Escape, Enter])
    add_director.prompt()

    mock_add_person_to_watchlist.assert_not_called()
