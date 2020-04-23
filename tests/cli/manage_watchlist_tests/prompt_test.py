import pytest
from pytest_mock import MockFixture

from movielog.cli import manage_watchlist
from tests.cli.keys import Down, End, Enter, Up
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_add_director(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.manage_watchlist.add_director.prompt")


@pytest.fixture(autouse=True)
def mock_add_performer(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.manage_watchlist.add_performer.prompt")


@pytest.fixture(autouse=True)
def mock_add_writer(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.manage_watchlist.add_writer.prompt")


@pytest.fixture(autouse=True)
def mock_add_to_collection(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.manage_watchlist.add_to_collection.prompt")


@pytest.fixture(autouse=True)
def mock_new_collection(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.manage_watchlist.new_collection.prompt")


@pytest.fixture(autouse=True)
def mock_watchlist_update_watchlist_titles_table(mocker: MockFixture) -> MockFixture:
    return mocker.patch(
        "movielog.cli.manage_watchlist.watchlist.update_watchlist_titles_table"
    )


def test_calls_add_director(
    mock_input: PosixPipeInput, mock_add_director: MockFixture
) -> None:
    mock_input.send_text("".join([Down, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_director.assert_called_once()


def test_calls_add_performer(
    mock_input: PosixPipeInput, mock_add_performer: MockFixture
) -> None:
    mock_input.send_text("".join([Down, Down, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_performer.assert_called_once()


def test_calls_add_writer(
    mock_input: PosixPipeInput, mock_add_writer: MockFixture
) -> None:
    mock_input.send_text("".join([Down, Down, Down, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_writer.assert_called_once()


def test_calls_add_to_collection(
    mock_input: PosixPipeInput, mock_add_to_collection: MockFixture
) -> None:
    mock_input.send_text("".join([Up, Up, Up, Enter, Enter]))
    manage_watchlist.prompt()

    mock_add_to_collection.assert_called_once()


def test_calls_new_collection(
    mock_input: PosixPipeInput, mock_new_collection: MockFixture
) -> None:
    mock_input.send_text("".join([Up, Up, Enter, Enter]))
    manage_watchlist.prompt()

    mock_new_collection.assert_called_once()


def test_calls_update_watchlist_titles_table(
    mock_input: PosixPipeInput,
    mock_watchlist_update_watchlist_titles_table: MockFixture,
) -> None:
    mock_input.send_text(f"{Up}{Enter}y{Enter}")
    manage_watchlist.prompt()

    mock_watchlist_update_watchlist_titles_table.assert_called_once()


def test_can_confirm_update_watchlist_titles_table(
    mock_input: PosixPipeInput,
    mock_watchlist_update_watchlist_titles_table: MockFixture,
) -> None:
    mock_input.send_text(f"{Up}{Enter}n{Enter}")
    manage_watchlist.prompt()

    mock_watchlist_update_watchlist_titles_table.assert_not_called()
