from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import imdb
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_update_datasets(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.imdb.repository_api.update_datasets")


@pytest.fixture(autouse=True)
def mock_update_title_data(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.imdb.update_title_data.prompt")


@pytest.fixture(autouse=True)
def mock_update_watchlist_credits(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.imdb.update_watchlist_credits.prompt")


@pytest.fixture(autouse=True)
def mock_validate_data(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.imdb.validate_data.prompt")


def test_calls_update_datasets(mock_input: MockInput, mock_update_datasets: MagicMock) -> None:
    mock_input([Enter, Escape, Escape])
    imdb.prompt()

    mock_update_datasets.assert_called_once()


def test_calls_mock_update_title_data(
    mock_input: MockInput, mock_update_title_data: MagicMock
) -> None:
    mock_input([Down, Enter, Escape, Escape])
    imdb.prompt()

    mock_update_title_data.assert_called_once()


def test_calls_update_watchlist_credits(
    mock_input: MockInput, mock_update_watchlist_credits: MagicMock
) -> None:
    mock_input([Down, Down, Enter, Escape, Escape])

    imdb.prompt()

    mock_update_watchlist_credits.assert_called_once()


def test_calls_validate_data(mock_input: MockInput, mock_validate_data: MagicMock) -> None:
    mock_input([Down, Down, Down, Enter, Escape, Escape])
    imdb.prompt()

    mock_validate_data.assert_called_once()
