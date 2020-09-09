import pytest
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def mock_imdb_call(mocker: MockerFixture) -> None:
    mocker.patch("movielog.imdb_http.credits_for_person", return_value=[])
