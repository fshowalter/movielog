from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_to_collection
from movielog.repository.api import Collection
from movielog.repository.datasets.dataset_title import DatasetTitle
from movielog.repository.db import titles_table
from tests.cli.conftest import MockInput
from tests.cli.keys import Escape
from tests.cli.prompt_utils import ConfirmType, enter_text, select_option


def enter_title(title: str) -> list[str]:
    return enter_text(title)


def select_collection() -> list[str]:
    return select_option(1)


def select_title_search_result(confirm: ConfirmType) -> list[str]:
    return select_option(1, confirm=confirm)


@pytest.fixture(autouse=True)
def seed_db() -> None:
    titles_table.reload(
        [
            DatasetTitle(
                imdb_id="tt0087298",
                title="Friday the 13th: The Final Chapter",
                full_title="Friday the 13th: The Final Chapter (1984)",
                original_title="Friday the 13th: The Final Chapter",
                year="1984",
                aka_titles=["Friday the 13th Part 4"],
                runtime_minutes=91,
                principal_cast=["Corey Feldman"],
                imdb_votes=32,
                imdb_rating=6.4,
            ),
            DatasetTitle(
                imdb_id="tt0089175",
                title="Fright Night",
                full_title="Fright Night (1985)",
                original_title="Fright Night",
                aka_titles=[],
                year="1985",
                runtime_minutes=90,
                principal_cast=["Chris Sarandon", "William Ragsdale"],
                imdb_votes=23,
                imdb_rating=4,
            ),
            DatasetTitle(
                imdb_id="tt0080761",
                title="Friday the 13th",
                full_title="Friday the 13th (1980)",
                original_title="Friday the 13th",
                year="1980",
                aka_titles=[],
                runtime_minutes=89,
                principal_cast=["Kevin Bacon"],
                imdb_votes=45,
                imdb_rating=7.4,
            ),
            DatasetTitle(
                imdb_id="tt0082418",
                title="Friday the 13th Part 2",
                full_title="Friday the 13th Part 2 (1981)",
                original_title="Friday the 13th Part 2",
                aka_titles=[],
                year="1981",
                runtime_minutes=90,
                principal_cast=["Amy Steel"],
                imdb_votes=34,
                imdb_rating=5.5,
            ),
            DatasetTitle(
                imdb_id="tt0083972",
                title="Friday the 13th Part III",
                full_title="Friday the 13th Part III (1982)",
                original_title="Friday the 13th Part 3",
                aka_titles=["Friday the 13th 3-D"],
                year="1982",
                runtime_minutes=87,
                principal_cast=["Larry Zerner"],
                imdb_votes=33,
                imdb_rating=4.9,
            ),
        ]
    )


@pytest.fixture(autouse=True)
def mock_add_title_to_collection(
    mocker: MockerFixture,
) -> tuple[Collection, MagicMock]:
    collection = Collection(
        name="Friday the 13th",
        slug="friday-the-13th",
        title_ids=set(["tt0080761", "tt0082418", "tt0083972"]),
        description="The Friday the 13th franchise.",
    )

    mocker.patch(
        "movielog.cli.add_to_collection.repository_api.watchlist_collections",
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
            *enter_title("The Final Chapter"),
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
