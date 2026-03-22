from unittest.mock import MagicMock

import pytest

from movielog.cli import manage_watchlist
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape, Up


@pytest.fixture(autouse=True)
def mock_add_director(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.manage_watchlist.add_director.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_add_performer(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.manage_watchlist.add_performer.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_add_writer(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.manage_watchlist.add_writer.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_add_to_collection(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.manage_watchlist.add_to_collection.prompt", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_new_collection(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("movielog.cli.manage_watchlist.new_collection.prompt", mock)
    return mock


def test_calls_add_director(mock_input: MockInput, mock_add_director: MagicMock) -> None:
    mock_input([Enter, Escape, Escape])
    manage_watchlist.prompt()

    mock_add_director.assert_called_once()


def test_calls_add_performer(mock_input: MockInput, mock_add_performer: MagicMock) -> None:
    mock_input([Down, Enter, Escape, Escape])
    manage_watchlist.prompt()

    mock_add_performer.assert_called_once()


def test_calls_add_writer(mock_input: MockInput, mock_add_writer: MagicMock) -> None:
    mock_input([Down, Down, Enter, Escape, Escape])
    manage_watchlist.prompt()

    mock_add_writer.assert_called_once()


def test_calls_add_to_collection(mock_input: MockInput, mock_add_to_collection: MagicMock) -> None:
    mock_input([Down, Down, Down, Enter, Escape, Escape])
    manage_watchlist.prompt()

    mock_add_to_collection.assert_called_once()


def test_calls_new_collection(mock_input: MockInput, mock_new_collection: MagicMock) -> None:
    mock_input([Up, Enter, Escape, Escape])
    manage_watchlist.prompt()

    mock_new_collection.assert_called_once()
