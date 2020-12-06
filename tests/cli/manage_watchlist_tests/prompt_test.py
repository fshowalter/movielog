from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import manage_watchlist
from tests.cli.keys import Down, Enter, Up
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_add_director(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.manage_watchlist.add_director.prompt")


@pytest.fixture(autouse=True)
def mock_add_performer(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.manage_watchlist.add_performer.prompt")


@pytest.fixture(autouse=True)
def mock_add_writer(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.manage_watchlist.add_writer.prompt")


@pytest.fixture(autouse=True)
def mock_add_to_collection(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.manage_watchlist.add_to_collection.prompt")


@pytest.fixture(autouse=True)
def mock_new_collection(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.manage_watchlist.new_collection.prompt")


def test_calls_add_director(
    mock_input: PosixPipeInput, mock_add_director: MagicMock
) -> None:
    mock_input.send_text("".join([Down, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_director.assert_called_once()


def test_calls_add_performer(
    mock_input: PosixPipeInput, mock_add_performer: MagicMock
) -> None:
    mock_input.send_text("".join([Down, Down, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_performer.assert_called_once()


def test_calls_add_writer(
    mock_input: PosixPipeInput, mock_add_writer: MagicMock
) -> None:
    mock_input.send_text("".join([Down, Down, Down, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_writer.assert_called_once()


def test_calls_add_to_collection(
    mock_input: PosixPipeInput, mock_add_to_collection: MagicMock
) -> None:
    mock_input.send_text("".join([Up, Up, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_to_collection.assert_called_once()


def test_calls_new_collection(
    mock_input: PosixPipeInput, mock_new_collection: MagicMock
) -> None:
    mock_input.send_text("".join([Up, Enter, Enter]))
    manage_watchlist.prompt()

    mock_new_collection.assert_called_once()
