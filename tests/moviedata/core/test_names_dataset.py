import os
from typing import Any, Callable
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.moviedata.core import movies_table, names_dataset
from tests.conftest import QueryResult


@pytest.fixture(autouse=True)
def downloader_mock(mocker: MockerFixture, gzip_file: MagicMock) -> Any:
    file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "people_test_data.tsv")
    )

    return mocker.patch(
        "movielog.moviedata.core.names_dataset.downloader.download",
        return_value=file_path,
    )


@pytest.fixture(autouse=True)
def seed_db() -> None:
    movies_table.reload(
        [
            movies_table.Row(
                imdb_id="tt0034583",
                title="Casablanca",
                original_title=None,
                year=1942,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=32,
                imdb_rating=7.4,
            ),
            movies_table.Row(
                imdb_id="tt0040506",
                title="Key Largo",
                original_title=None,
                year=1948,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=23,
                imdb_rating=7.1,
            ),
            movies_table.Row(
                imdb_id="tt0053198",
                title="The 400 Blows",
                original_title=None,
                year=1959,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=16,
                imdb_rating=8.1,
            ),
            movies_table.Row(
                imdb_id="tt0054135",
                title="Ocean's 11",
                original_title=None,
                year=1960,
                runtime_minutes=None,
                principal_cast_ids=None,
                votes=11,
                imdb_rating=6,
            ),
        ]
    )


def test_inserts_people_from_names_dataset(
    sql_query: Callable[[str], QueryResult]
) -> None:
    expected = [
        {
            "imdb_id": "nm0000007",
            "full_name": "Humphrey Bogart",
            "known_for_title_ids": "tt0034583,tt0040506",
        },
        {
            "imdb_id": "nm0000064",
            "full_name": "Edward G. Robinson",
            "known_for_title_ids": "tt0040506",
        },
        {
            "imdb_id": "nm0000076",
            "full_name": "François Truffaut",
            "known_for_title_ids": "tt0053198",
        },
        {
            "imdb_id": "nm0002035",
            "full_name": "Sammy Davis Jr.",
            "known_for_title_ids": "tt0054135",
        },
    ]

    names_dataset.refresh()

    assert sql_query("SELECT * FROM 'people' order by imdb_id;") == expected
