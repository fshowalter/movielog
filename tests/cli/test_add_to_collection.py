from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_to_collection
from movielog.repository.api import Collection
from movielog.repository.imdb_http_title import TitlePage
from tests.cli.conftest import MockInput
from tests.cli.keys import Escape
from tests.cli.prompt_utils import ConfirmType, enter_text, select_option


def enter_token() -> list[str]:
    return enter_text("a-test-aws-token")


def enter_title(title: str) -> list[str]:
    return enter_text(title)


def select_collection() -> list[str]:
    return select_option(1)


def select_title_search_result(confirm: ConfirmType) -> list[str]:
    return select_option(1, confirm=confirm)


@pytest.fixture(autouse=True)
def mock_search_title(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "movielog.cli.title_searcher.repository_api.get_title_page",
        return_value=TitlePage(
            imdb_id="tt0087298",
            title="Friday the 13th: The Final Chapter",
            year=1984,
            principal_cast=["Erich Anderson", "Judie Aronson", "Peter Barton"],
            genres=["Horror", "Thriller"],
            release_date="1984-04-13",
            release_date_country="USA",
            original_title="Friday the 13th: The Final Chapter",
            countries=["USA"],
            runtime_minutes=91,
            credits={},
        ),
    )


@pytest.fixture(autouse=True)
def mock_add_title_to_collection(
    mocker: MockerFixture,
) -> tuple[Collection, MagicMock]:
    collection = Collection(
        name="Friday the 13th",
        slug="friday-the-13th",
        title_ids={"tt0080761", "tt0082418", "tt0083972"},
        description="The Friday the 13th franchise.",
    )

    mocker.patch(
        "movielog.cli.add_to_collection.repository_api.collections",
        return_value=[collection],
    )

    return (
        collection,
        mocker.patch(
            "movielog.cli.add_to_collection.repository_api.add_title_to_collection",
            return_value=[collection],
        ),
    )


def test_calls_add_title_to_collection(
    mock_input: MockInput,
    mock_add_title_to_collection: tuple[Collection, MagicMock],
) -> None:
    mock_input(
        [
            *select_collection(),
            *enter_token(),
            *enter_title("tt0087298"),
            *select_title_search_result(confirm="y"),
            Escape,
            Escape,
        ]
    )
    add_to_collection.prompt()

    collection, mock = mock_add_title_to_collection

    mock.assert_called_once_with(
        collection=collection,
        imdb_id="tt0087298",
        full_title="Friday the 13th: The Final Chapter (1984)",
    )


def test_does_not_call_add_title_to_collection_if_no_selection(
    mock_input: MockInput,
    mock_add_title_to_collection: tuple[Collection, MagicMock],
) -> None:
    mock_input(
        [
            *select_collection(),
            *enter_token(),
            *enter_title("The Final Chapter"),
            Escape,
            Escape,
            Escape,
            Escape,
        ]
    )
    add_to_collection.prompt()

    _collection, mock = mock_add_title_to_collection

    mock.assert_not_called()
