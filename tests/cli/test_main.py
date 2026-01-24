from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import main
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape, Up


@pytest.fixture(autouse=True)
def mock_add_viewing(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.add_viewing.prompt")


@pytest.fixture(autouse=True)
def mock_imdb(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.imdb.prompt")


@pytest.fixture(autouse=True)
def mock_manage_watchlist(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.manage_watchlist.prompt")


@pytest.fixture(autouse=True)
def mock_manage_collections(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.manage_collections.prompt")


@pytest.fixture(autouse=True)
def mock_export_data(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.export_data.prompt")


def test_calls_add_viewing(mock_input: MockInput, mock_add_viewing: MagicMock) -> None:
    mock_input([Enter, Escape, Escape])
    main.prompt()

    mock_add_viewing.assert_called_once()


def test_calls_imdb(mock_input: MockInput, mock_imdb: MagicMock) -> None:
    mock_input([Down, Down, Down, Enter, Escape, Escape])
    main.prompt()

    mock_imdb.assert_called_once()


def test_calls_manage_watchlist(mock_input: MockInput, mock_manage_watchlist: MagicMock) -> None:
    mock_input([Down, Enter, Escape, Escape])
    main.prompt()

    mock_manage_watchlist.assert_called_once()


def test_calls_manage_collections(
    mock_input: MockInput, mock_manage_collections: MagicMock
) -> None:
    mock_input([Down, Down, Enter, Escape, Escape])
    main.prompt()

    mock_manage_collections.assert_called_once()


def test_calls_export_data(
    mock_input: MockInput,
    mock_export_data: MagicMock,
) -> None:
    mock_input([Up, Enter, Escape, Escape])
    main.prompt()

    mock_export_data.assert_called_once()
