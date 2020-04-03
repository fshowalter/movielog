import os
from typing import Any, Set

import pytest
from pytest_mock import MockFixture

from movielog import aka_titles


@pytest.fixture(autouse=True)
def imdb_s3_download_mock(mocker: MockFixture, gzip_file: MockFixture) -> Any:
    file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "aka_titles_test_data.tsv")
    )

    return mocker.patch(
        "movielog.aka_titles.imdb_s3_downloader.download", return_value=file_path
    )


@pytest.fixture(autouse=True)
def movie_ids_mock(mocker: MockFixture) -> Any:
    valid_ids: Set[str] = set(["tt0053221", "tt0089175"])
    mocker.patch("movielog.aka_titles.movies.title_ids", return_value=valid_ids)


def test_inserts_people_from_downloaded_s3_file(sql_query: MockFixture) -> None:
    expected = [
        (1, "tt0053221", 26, "リオ・ブラボー", "JP", "ja", "imdbDisplay", None, 0,),
        (2, "tt0053221", 28, "Ρίο Μπράβο", "GR", None, "imdbDisplay", None, 0,),
        (
            3,
            "tt0053221",
            33,
            "Howard Hawks' Rio Bravo",
            "US",
            None,
            None,
            "complete title",
            0,
        ),
        (
            4,
            "tt0089175",
            10,
            "Fright Night - Die rabenschwarze Nacht",
            "XWG",
            None,
            None,
            None,
            0,
        ),
        (5, "tt0089175", 13, "Night of Horror", "PK", "en", None, "poster title", 0,),
    ]

    aka_titles.update()

    assert sql_query("SELECT * FROM 'aka_titles';") == expected
