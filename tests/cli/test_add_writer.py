from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_writer
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
            imdb_id="nm0102824",
            name="Leigh Brackett",
            known_for_titles=["Rio Bravo", "The Big Sleep", "The Empire Strikes Back"],
        ),
    )


def test_calls_add_writer(mock_input: MockInput, mock_add_person_to_watchlist: MagicMock) -> None:
    mock_input(["nm0102824", Enter, Down, Enter, "y", Enter])
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
