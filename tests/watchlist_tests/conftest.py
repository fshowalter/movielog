import pytest
from pytest_mock import MockFixture


@pytest.fixture(autouse=True)
def mock_imdb_call(mocker: MockFixture) -> None:
    mocker.patch("movielog.imdb_http.credits_for_person", return_value=[])
