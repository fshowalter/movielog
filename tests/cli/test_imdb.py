from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import imdb
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def mock_refresh_core_data(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.imdb.movielog_api.refresh_core_data")


@pytest.fixture(autouse=True)
def mock_refresh_credits(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.imdb.movielog_api.refresh_credits")


def test_calls_refresh_core_data(
    mock_input: MockInput, mock_refresh_core_data: MagicMock
) -> None:
    mock_input([Down, Enter, "y", Enter, Escape])
    imdb.prompt()

    mock_refresh_core_data.assert_called_once()


def test_can_confirm_refresh_core_data(
    mock_input: MockInput, mock_refresh_core_data: MagicMock
) -> None:
    mock_input([Down, Enter, "n", Enter, Escape])
    imdb.prompt()

    mock_refresh_core_data.assert_not_called()


def test_calls_refresh_credits(
    mock_input: MockInput, mock_refresh_credits: MagicMock
) -> None:
    mock_input([Down, Down, Enter, "y", Enter, Escape])
    imdb.prompt()

    mock_refresh_credits.assert_called_once()


def test_can_confirm_refresh_credits(
    mock_input: MockInput, mock_refresh_credits: MagicMock
) -> None:
    mock_input([Down, Down, Enter, "n", Enter, Escape])
    imdb.prompt()

    mock_refresh_credits.assert_not_called()
