import pytest
from pytest_mock import MockFixture


@pytest.fixture(autouse=True)
def performing_credits_update_mock(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.viewings.performing_credits.update")
