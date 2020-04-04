import os
from typing import Any, Set

import pytest
from pytest_mock import MockFixture

from movielog import movies


@pytest.fixture(autouse=True)
def imdb_s3_download_mock(mocker: MockFixture, gzip_file: MockFixture) -> Any:
    file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "movies_test_data.tsv")
    )

    return mocker.patch(
        "movielog.movies.imdb_s3_downloader.download", return_value=file_path
    )


def test_inserts_movies_from_downloaded_s3_file(sql_query: MockFixture) -> None:
    expected = [
        ("tt0053221", "Rio Bravo", "Rio Bravo", 1959, 141, None),
        (
            "tt0050280",
            "The Curse of Frankenstein",
            "The Curse of Frankenstein",
            1957,
            82,
            None,
        ),
        ("tt0051554", "Horror of Dracula", "Dracula", 1958, 82, None),
        ("tt0089175", "Fright Night", "Fright Night", 1985, 106, None),
        ("tt0116671", "Jack Frost", "Jack Frost", 1997, 89, None),
    ]

    movies.update()

    assert sql_query("SELECT * FROM 'movies';") == expected


def test_clears_update_ids_cache() -> None:
    expected = set(["tt0053221", "tt0050280", "tt0051554", "tt0089175", "tt0116671"])

    movies.MoviesTable.recreate()

    assert movies.title_ids() == set()

    movies.update()

    assert movies.title_ids() == expected
