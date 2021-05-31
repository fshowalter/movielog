from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import new_collection
from tests.cli.conftest import MockInput
from tests.cli.keys import Enter, Escape


@pytest.fixture(autouse=True)
def mock_add_collection(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.new_collection.movielog_api.add_collection")


def test_calls_add_collection(
    mock_input: MockInput, mock_add_collection: MagicMock
) -> None:
    mock_input(["Halloween", Enter, "y"])
    new_collection.prompt()

    mock_add_collection.assert_called_once_with("Halloween")


def test_does_not_call_add_viewing_if_no_movie(
    mock_input: MockInput, mock_add_collection: MagicMock
) -> None:
    mock_input([Escape])
    new_collection.prompt()

    mock_add_collection.assert_not_called()


def test_can_confirm_collection_name(
    mock_input: MockInput, mock_add_collection: MagicMock
) -> None:
    mock_input(["Halloween", Enter, "n"])
    new_collection.prompt()

    mock_add_collection.assert_not_called()
