import os
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.moviedata.core import titles_dataset
from tests.conftest import QueryResult


@pytest.fixture(autouse=True)
def downloader_mock(mocker: MockerFixture, gzip_file: MagicMock) -> Any:
    movies_file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "movies_test_data.tsv")
    )

    principals_file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "principals_test_data.tsv")
    )

    ratings_file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "ratings_test_data.tsv")
    )

    return mocker.patch(
        "movielog.moviedata.core.downloader.download",
        side_effect=[movies_file_path, principals_file_path, ratings_file_path],
    )


def test_inserts_movies_from_dataset(sql_query: Callable[[str], QueryResult]) -> None:
    expected = [
        {
            "imdb_id": "tt0050280",
            "title": "The Curse of Frankenstein",
            "original_title": "The Curse of Frankenstein",
            "year": 1957,
            "runtime_minutes": 82,
            "principal_cast_ids": "nm0001088",
            "votes": 23,
            "imdb_rating": 6.7,
        },
        {
            "imdb_id": "tt0051554",
            "title": "Horror of Dracula",
            "original_title": "Dracula",
            "year": 1958,
            "runtime_minutes": 82,
            "principal_cast_ids": "nm0001088",
            "votes": 32,
            "imdb_rating": 4.7,
        },
        {
            "imdb_id": "tt0053221",
            "title": "Rio Bravo",
            "original_title": "Rio Bravo",
            "year": 1959,
            "runtime_minutes": 141,
            "principal_cast_ids": "nm0000078,nm0001509,nm0625699",
            "votes": 16,
            "imdb_rating": 5.7,
        },
        {
            "imdb_id": "tt0089175",
            "title": "Fright Night",
            "original_title": "Fright Night",
            "year": 1985,
            "runtime_minutes": 106,
            "principal_cast_ids": "nm0001697",
            "votes": 44,
            "imdb_rating": 7.72,
        },
        {
            "imdb_id": "tt0116671",
            "title": "Jack Frost",
            "original_title": "Jack Frost",
            "year": 1997,
            "runtime_minutes": 89,
            "principal_cast_ids": "nm0531924",
            "votes": 3,
            "imdb_rating": 4.0,
        },
    ]

    titles_dataset.refresh()

    assert sql_query("SELECT * FROM 'movies' order by imdb_id;") == expected
