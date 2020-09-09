import os
from typing import Any

import pytest
from pytest_mock import MockerFixture

from movielog import movies


@pytest.fixture(autouse=True)
def imdb_s3_download_mock(mocker: MockerFixture, gzip_file: MockerFixture) -> Any:
    movies_file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "movies_test_data.tsv")
    )

    principals_file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "principals_test_data.tsv")
    )

    return mocker.patch(
        "movielog.movies.imdb_s3_downloader.download",
        side_effect=[movies_file_path, principals_file_path],
    )


def test_inserts_movies_from_downloaded_s3_file(sql_query: MockerFixture) -> None:
    expected = [
        (
            "tt0053221",
            "Rio Bravo",
            "Rio Bravo",
            1959,
            141,
            "nm0000078,nm0001509,nm0625699",
        ),
        (
            "tt0050280",
            "The Curse of Frankenstein",
            "The Curse of Frankenstein",
            1957,
            82,
            "nm0001088",
        ),
        ("tt0051554", "Horror of Dracula", "Dracula", 1958, 82, "nm0001088"),
        ("tt0089175", "Fright Night", "Fright Night", 1985, 106, "nm0001697"),
        ("tt0116671", "Jack Frost", "Jack Frost", 1997, 89, "nm0531924"),
    ]

    movies.update()

    assert sql_query("SELECT * FROM 'movies';") == expected


def test_clears_update_ids_cache() -> None:
    expected = set(["tt0053221", "tt0050280", "tt0051554", "tt0089175", "tt0116671"])

    movies.MoviesTable.recreate()

    assert movies.title_ids() == set()

    movies.update()

    assert movies.title_ids() == expected
