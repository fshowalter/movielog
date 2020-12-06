from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import main
from tests.cli.keys import ControlD, Down, End, Enter, Up
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_add_viewing(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.add_viewing.prompt")


@pytest.fixture(autouse=True)
def mock_manage_watchlist(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.manage_watchlist.prompt")


@pytest.fixture(autouse=True)
def mock_exporter_export(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.cli.main.exporter.export")


def test_calls_add_viewing(
    mock_input: PosixPipeInput, mock_add_viewing: MagicMock
) -> None:
    mock_input.send_text("".join([Enter, ControlD]))
    main.prompt()

    mock_add_viewing.assert_called_once()


def test_calls_manage_watchlist(
    mock_input: PosixPipeInput, mock_manage_watchlist: MagicMock
) -> None:
    mock_input.send_text("".join([Down, Enter, End, Enter]))
    main.prompt()

    mock_manage_watchlist.assert_called_once()


def test_calls_exporter_export(
    mock_input: PosixPipeInput,
    mock_exporter_export: MagicMock,
) -> None:
    mock_input.send_text(f"{Up}{Up}{Enter}y{Up}{Enter}")
    main.prompt()

    mock_exporter_export.assert_called_once()


def test_can_confirm_exporter_export(
    mock_input: PosixPipeInput,
    mock_exporter_export: MagicMock,
) -> None:
    mock_input.send_text(f"{Up}{Up}{Enter}n{Up}{Enter}")
    main.prompt()

    mock_exporter_export.assert_not_called()
