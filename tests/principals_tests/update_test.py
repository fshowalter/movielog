import os
from typing import Any, Set

import pytest
from pytest_mock import MockFixture

from movielog import principals


@pytest.fixture(autouse=True)
def imdb_s3_download_mock(mocker: MockFixture, gzip_file: MockFixture) -> Any:
    file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "principals_test_data.tsv")
    )

    return mocker.patch(
        "movielog.principals.imdb_s3_downloader.download", return_value=file_path
    )


@pytest.fixture(autouse=True)
def movie_ids_mock(mocker: MockFixture) -> Any:
    valid_ids: Set[str] = set(["tt0053221"])
    mocker.patch("movielog.principals.movies.title_ids", return_value=valid_ids)


def test_inserts_principals_from_downloaded_s3_file(sql_query: MockFixture,) -> None:
    expected = [
        (1, "tt0053221", "nm0000078", 1, "actor", None, '["Sheriff John T. Chance"]'),
        (2, "tt0053221", "nm0001509", 2, "actor", None, "[\"Dude ('Borrachón')\"]"),
        (3, "tt0053221", "nm0625699", 3, "actor", None, '["Colorado Ryan"]'),
        (4, "tt0053221", "nm0001141", 4, "actress", None, '["Feathers"]'),
    ]

    principals.update()

    assert sql_query("SELECT * FROM 'principals';") == expected
