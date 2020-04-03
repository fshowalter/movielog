import os
from typing import Any, Set

import pytest
from pytest_mock import MockFixture

from movielog import people


@pytest.fixture(autouse=True)
def imdb_s3_download_mock(mocker: MockFixture, gzip_file: MockFixture) -> Any:
    file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "people_test_data.tsv")
    )

    return mocker.patch(
        "movielog.people.imdb_s3_downloader.download", return_value=file_path
    )


@pytest.fixture(autouse=True)
def movie_ids_mock(mocker: MockFixture) -> Any:
    valid_ids: Set[str] = set(
        ["tt0037382", "tt0041452", "tt0021079", "tt0053198", "tt0087032", "tt0100140"]
    )
    mocker.patch("movielog.people.movies.title_ids", return_value=valid_ids)


def test_inserts_people_from_downloaded_s3_file(sql_query: MockFixture,) -> None:
    expected = [
        (
            "nm0000007",
            "Humphrey Bogart",
            "Bogart",
            "Humphrey",
            None,
            None,
            "actor,soundtrack,producer",
            "tt0037382,tt0043265,tt0034583,tt0033870",
        ),
        (
            "nm0000014",
            "Olivia de Havilland",
            "de Havilland",
            "Olivia",
            None,
            None,
            "actress,soundtrack",
            "tt0031381,tt0029843,tt0041452,tt0040806",
        ),
        (
            "nm0000064",
            "Edward G. Robinson",
            "Robinson",
            "Edward G.",
            None,
            None,
            "actor,soundtrack,writer",
            "tt0036775,tt0021079,tt0040506,tt0049833",
        ),
        (
            "nm0000076",
            "François Truffaut",
            "Truffaut",
            "François",
            None,
            None,
            "writer,director,producer",
            "tt0053198,tt0055032,tt0070460,tt0075860",
        ),
        (
            "nm0002035",
            "Sammy Davis Jr.",
            "Davis Jr.",
            "Sammy",
            None,
            None,
            "soundtrack,actor,producer",
            "tt0082136,tt0053182,tt0066183,tt0087032",
        ),
        (
            "nm0000333",
            "Cher",
            "",
            "Cher",
            None,
            None,
            "soundtrack,actress,director",
            "tt0086312,tt0093565,tt1126591,tt0100140",
        ),
    ]

    people.update()

    assert sql_query("SELECT * FROM 'people';") == expected
