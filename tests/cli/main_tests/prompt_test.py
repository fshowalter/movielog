import pytest
from pytest_mock import MockFixture

from movielog.cli import main
from tests.cli.keys import ControlD, Down, End, Enter, Up
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_add_viewing(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.add_viewing.prompt")


@pytest.fixture(autouse=True)
def mock_manage_watchlist(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.manage_watchlist.prompt")


@pytest.fixture(autouse=True)
def mock_update_imdb_data(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.update_imdb_data.prompt")


@pytest.fixture(autouse=True)
def mock_update_viewings(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.update_viewings.prompt")


def test_calls_add_viewing(
    mock_input: PosixPipeInput, mock_add_viewing: MockFixture
) -> None:
    mock_input.send_text("".join([Enter, ControlD]))
    main.prompt()

    mock_add_viewing.assert_called_once()


def test_calls_manage_watchlist(
    mock_input: PosixPipeInput, mock_manage_watchlist: MockFixture
) -> None:
    mock_input.send_text("".join([Down, Enter, End, Enter]))
    main.prompt()

    mock_manage_watchlist.assert_called_once()


def test_calls_update_imdb_data(
    mock_input: PosixPipeInput, mock_update_imdb_data: MockFixture
) -> None:
    mock_input.send_text("".join([Down, Down, Enter, End, Enter]))
    main.prompt()

    mock_update_imdb_data.assert_called_once()


def test_calls_update_viewings(
    mock_input: PosixPipeInput, mock_update_viewings: MockFixture
) -> None:
    mock_input.send_text("".join([Up, Up, Enter, End, Enter]))
    main.prompt()

    mock_update_viewings.assert_called_once()
