import os
from typing import Any, Callable, Set
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.moviedata.core import title_akas_dataset
from tests.conftest import QueryResult


@pytest.fixture(autouse=True)
def downloader_mock(mocker: MockerFixture, gzip_file: MagicMock) -> Any:
    file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "aka_titles_test_data.tsv")
    )

    return mocker.patch(
        "movielog.moviedata.core.title_akas_dataset.downloader.download",
        return_value=file_path,
    )


@pytest.fixture(autouse=True)
def movie_ids_mock(mocker: MockerFixture) -> Any:
    valid_ids: Set[str] = set(["tt0053221", "tt0089175"])
    mocker.patch(
        "movielog.moviedata.core.title_akas_dataset.movies_table.movie_ids",
        return_value=valid_ids,
    )


def test_inserts_people_from_dataset(sql_query: Callable[[str], QueryResult]) -> None:

    expected = [
        {
            "id": 1,
            "movie_imdb_id": "tt0053221",
            "sequence": 26,
            "title": "リオ・ブラボー",
            "region": "JP",
            "language": "ja",
            "types": "imdbDisplay",
            "attributes": None,
            "is_original_title": 0,
        },
        {
            "id": 2,
            "movie_imdb_id": "tt0053221",
            "sequence": 28,
            "title": "Ρίο Μπράβο",
            "region": "GR",
            "language": None,
            "types": "imdbDisplay",
            "attributes": None,
            "is_original_title": 0,
        },
        {
            "id": 3,
            "movie_imdb_id": "tt0053221",
            "sequence": 33,
            "title": "Howard Hawks' Rio Bravo",
            "region": "US",
            "language": None,
            "types": None,
            "attributes": "complete title",
            "is_original_title": 0,
        },
        {
            "id": 4,
            "movie_imdb_id": "tt0089175",
            "sequence": 10,
            "title": "Fright Night - Die rabenschwarze Nacht",
            "region": "XWG",
            "language": None,
            "types": None,
            "attributes": None,
            "is_original_title": 0,
        },
        {
            "id": 5,
            "movie_imdb_id": "tt0089175",
            "sequence": 13,
            "title": "Night of Horror",
            "region": "PK",
            "language": "en",
            "types": None,
            "attributes": "poster title",
            "is_original_title": 0,
        },
    ]

    title_akas_dataset.refresh()

    assert sql_query("SELECT * FROM 'aka_titles' order by id;") == expected
