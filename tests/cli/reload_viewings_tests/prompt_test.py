import pytest
from pytest_mock import MockFixture

from movielog.cli import reload_viewings
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_viewings_update(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.reload_viewings.viewings.update")


def test_calls_viewings_update(
    mock_input: PosixPipeInput, mock_viewings_update: MockFixture
) -> None:
    mock_input.send_text(f"y")  # noqa: WPS221
    reload_viewings.prompt()

    mock_viewings_update.assert_called_once_with()


def test_can_confirm_update(
    mock_input: PosixPipeInput, mock_viewings_update: MockFixture
) -> None:
    mock_input.send_text(f"n")  # noqa: WPS221
    reload_viewings.prompt()

    mock_viewings_update.assert_not_called()
