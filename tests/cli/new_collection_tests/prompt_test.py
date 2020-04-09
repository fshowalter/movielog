import pytest
from pytest_mock import MockFixture

from movielog.cli import new_collection
from tests.cli.keys import Enter, Escape
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_watchlist_add_collection(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.new_collection.watchlist.add_collection")


def test_calls_add_collection(
    mock_input: PosixPipeInput, mock_watchlist_add_collection: MockFixture
) -> None:
    mock_input.send_text(f"Halloween{Enter}y")  # noqa: WPS221
    new_collection.prompt()

    mock_watchlist_add_collection.assert_called_once_with("Halloween")


def test_does_not_call_add_viewing_if_no_movie(
    mock_input: PosixPipeInput, mock_watchlist_add_collection: MockFixture
) -> None:
    mock_input.send_text(f"{Escape}")  # noqa: WPS221
    new_collection.prompt()

    mock_watchlist_add_collection.assert_not_called()


def test_can_confirm_collection_name(
    mock_input: PosixPipeInput, mock_watchlist_add_collection: MockFixture
) -> None:
    mock_input.send_text(f"Halloween{Enter}n")  # noqa: WPS221
    new_collection.prompt()

    mock_watchlist_add_collection.assert_not_called()
