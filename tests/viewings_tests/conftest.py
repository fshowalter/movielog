from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def performing_credits_update_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.viewings.performing_credits.update")
