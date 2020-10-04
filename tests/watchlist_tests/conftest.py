from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def mock_imdb_call(mocker: MockerFixture) -> None:
    mocker.patch("movielog.imdb_http.credits_for_person", return_value=[])


@pytest.fixture(autouse=True)
def release_dates_update_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.watchlist.release_dates.update")
