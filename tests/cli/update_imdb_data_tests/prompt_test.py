import pytest
from pytest_mock import MockFixture

from movielog.cli import update_imdb_data
from tests.cli.keys import Down, Enter
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_imdb_s3_orchestrator_orchestrate_update(mocker: MockFixture) -> MockFixture:
    return mocker.patch(
        "movielog.cli.update_imdb_data.imdb_s3_orchestrator.orchestrate_update"
    )


@pytest.fixture(autouse=True)
def mock_watchlist_update_watchlist_titles_table(mocker: MockFixture) -> MockFixture:
    return mocker.patch(
        "movielog.cli.update_imdb_data.watchlist.update_watchlist_titles_table"
    )


def test_callsimdb_s3_orchestrator_update(
    mock_input: PosixPipeInput,
    mock_imdb_s3_orchestrator_orchestrate_update: MockFixture,
) -> None:
    mock_input.send_text(f"{Down}{Enter}y{Enter}")
    update_imdb_data.prompt()

    mock_imdb_s3_orchestrator_orchestrate_update.assert_called_once()


def test_calls_update_imdb_web_data(
    mock_input: PosixPipeInput,
    mock_watchlist_update_watchlist_titles_table: MockFixture,
) -> None:
    mock_input.send_text(f"{Down}{Down}{Enter}y{Enter}")
    update_imdb_data.prompt()

    mock_watchlist_update_watchlist_titles_table.assert_called_once()
