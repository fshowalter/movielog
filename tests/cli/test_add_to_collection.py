from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.cli import add_to_collection
from movielog.moviedata.core import movies_table, people_table
from movielog.watchlist.collections import Collection
from movielog.watchlist.movies import Movie
from tests.cli.conftest import MockInput
from tests.cli.keys import Down, Enter, Escape


@pytest.fixture(autouse=True)
def seed_db() -> None:
    people_table.reload(
        [
            people_table.Row(
                imdb_id="nm0000397",
                full_name="Corey Feldman",
                known_for_title_ids="tt0087298",
            ),
            people_table.Row(
                imdb_id="nm0658133",
                full_name="Betsy Palmer",
                known_for_title_ids="tt0080761",
            ),
            people_table.Row(
                imdb_id="nm0824386",
                full_name="Amy Steel",
                known_for_title_ids="tt0082418",
            ),
            people_table.Row(
                imdb_id="nm0050676",
                full_name="Terry Ballard",
                known_for_title_ids="tt0083972",
            ),
        ]
    )

    movies_table.reload(
        [
            movies_table.Row(
                imdb_id="tt0087298",
                title="Friday the 13th: The Final Chapter",
                original_title="Friday the 13th: The Final Chapter",
                year=1984,
                runtime_minutes=None,
                principal_cast_ids="nm0000397, nm0000000",
                votes=32,
                imdb_rating=6.4,
            ),
            movies_table.Row(
                imdb_id="tt0089175",
                title="Fright Night",
                original_title="Fright Night",
                year=1985,
                runtime_minutes=None,
                principal_cast_ids="nm0001697",
                votes=23,
                imdb_rating=4,
            ),
            movies_table.Row(
                imdb_id="tt0080761",
                title="Friday the 13th",
                original_title="Friday the 13th",
                year=1980,
                runtime_minutes=None,
                principal_cast_ids="nm0658133",
                votes=45,
                imdb_rating=7.4,
            ),
            movies_table.Row(
                imdb_id="tt0082418",
                title="Friday the 13th Part 2",
                original_title="Friday the 13th Part 2",
                year=1981,
                runtime_minutes=None,
                principal_cast_ids="nm0824386",
                votes=34,
                imdb_rating=5.5,
            ),
            movies_table.Row(
                imdb_id="tt0083972",
                title="Friday the 13th Part III",
                original_title="Friday the 13th Part 3",
                year=1982,
                runtime_minutes=None,
                principal_cast_ids="nm0050676",
                votes=33,
                imdb_rating=4.9,
            ),
        ]
    )


@pytest.fixture(autouse=True)
def mock_add_movie_to_collection(mocker: MockerFixture) -> tuple[Collection, MagicMock]:
    collection = Collection(
        name="Friday the 13th",
        slug="friday-the-13th",
        movies=[
            Movie(imdb_id="tt0080761", year=1980, title="Friday the 13th"),
            Movie(imdb_id="tt0082418", year=1981, title="Friday the 13th Part 2"),
            Movie(imdb_id="tt0083972", year=1982, title="Friday the 13th Part III"),
        ],
    )

    mocker.patch(
        "movielog.cli.add_to_collection.movielog_api.collections",
        return_value=[collection],
    )

    return (
        collection,
        mocker.patch(
            "movielog.cli.add_to_collection.movielog_api.add_movie_to_collection",
            return_value=[collection],
        ),
    )


def test_calls_add_movie_to_collection(
    mock_input: MockInput, mock_add_movie_to_collection: tuple[Collection, MagicMock]
) -> None:
    mock_input([Down, Enter, "The Final Chapter", Enter, Down, Enter, "y", Enter])
    add_to_collection.prompt()

    collection, mock = mock_add_movie_to_collection

    mock.assert_called_once_with(
        collection=collection,
        imdb_id="tt0087298",
        title="Friday the 13th: The Final Chapter",
        year=1984,
    )


def test_does_not_call_add_movie_to_collection_if_no_selection(
    mock_input: MockInput, mock_add_movie_to_collection: tuple[Collection, MagicMock]
) -> None:
    mock_input([Down, Enter, Escape, Escape, Enter])
    add_to_collection.prompt()

    _collection, mock = mock_add_movie_to_collection

    mock.assert_not_called()
