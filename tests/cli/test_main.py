from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import main
from tests.cli.conftest import MockInput
from tests.cli.keys import ControlD, Down, End, Enter, Up


@pytest.fixture(autouse=True)
def mock_add_review(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.add_review.prompt")


@pytest.fixture(autouse=True)
def mock_imdb(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.imdb.prompt")


@pytest.fixture(autouse=True)
def mock_manage_watchlist(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.manage_watchlist.prompt")


@pytest.fixture(autouse=True)
def mock_export_data(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.movielog_api.export_data")


def test_calls_add_viewing(mock_input: MockInput, mock_add_review: MagicMock) -> None:
    mock_input([Enter, ControlD])
    main.prompt()

    mock_add_review.assert_called_once()


def test_calls_manage_watchlist(
    mock_input: MockInput, mock_manage_watchlist: MagicMock
) -> None:
    mock_input([Down, Enter, End, Enter])
    main.prompt()

    mock_manage_watchlist.assert_called_once()


def test_calls_export_data(
    mock_input: MockInput,
    mock_export_data: MagicMock,
) -> None:
    mock_input([Up, Up, Enter, "y", Up, Enter])
    main.prompt()

    mock_export_data.assert_called_once()


def test_can_confirm_export_data(
    mock_input: MockInput,
    mock_export_data: MagicMock,
) -> None:
    mock_input([Up, Up, Enter, "n", Up, Enter])
    main.prompt()

    mock_export_data.assert_not_called()
