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


def test_removes_movies_not_in_given_iterable(sql_query: MockerFixture) -> None:
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

    movies.remove_movies_not_in(["tt0089175"])

    assert sql_query("SELECT * FROM 'movies';") == [
        ("tt0089175", "Fright Night", "Fright Night", 1985, 106, "nm0001697"),
    ]
