from unittest.mock import MagicMock

import pytest

from movielog.cli import main
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape, Up


@pytest.fixture(autouse=True)
def mock_add_viewing(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.main.add_viewing.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_imdb(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.main.imdb.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_manage_watchlist(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.main.manage_watchlist.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_manage_collections(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.main.manage_collections.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_export_data(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.main.export_data.prompt", mock)
    return mock


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
