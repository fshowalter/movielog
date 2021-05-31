from datetime import date
from unittest.mock import MagicMock

import imdb
import pytest
from pytest_mock import MockerFixture

from movielog.moviedata.extended import cast, directors, movies, writers


@pytest.fixture(autouse=True)
def imdb_http_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(
        movies.imdb_http,
        "get_movie",
        return_value={
            "imdbID": "0092106",
            "title": "The Transformers: The Movie",
            "year": 1986,
            "countries": [
                "United States",
                "Japan",
            ],
            "raw release dates": [
                {
                    "country": "USA\n",
                    "date": "8 August 1986",
                },
            ],
            "cast": [
                imdb.Person.Person(
                    personID="0191520",
                    name="Peter Cullen",
                    notes="(voice)",
                    currentRole=["Optimus Prime", "Ironhide"],
                ),
                imdb.Person.Person(
                    personID="0000080",
                    name="Orson Welles",
                    notes="(voice)",
                    currentRole="Unicrom",
                ),
            ],
            "writers": [
                imdb.Person.Person(
                    personID="0295357",
                    name="Ron Friedman",
                    notes="(written by)",
                ),
            ],
            "directors": [
                imdb.Person.Person(
                    personID="0793802",
                    name="Nelson Shin",
                    notes="",
                ),
            ],
        },
    )


def test_fetch_parses_imdb_data(
    imdb_http_mock: MagicMock,
) -> None:
    expected = movies.Movie(
        imdb_id="tt0092106",
        sort_title="Transformers: The Movie (1986)",
        release_date=date(1986, 8, 8),
        release_date_notes="",
        countries=["United States", "Japan"],
        directors=[
            directors.Credit(
                person_imdb_id="nm0793802",
                name="Nelson Shin",
                sequence=0,
                notes="",
            )
        ],
        cast=[
            cast.Credit(
                person_imdb_id="nm0191520",
                name="Peter Cullen",
                roles=["Optimus Prime", "Ironhide"],
                notes="(voice)",
                sequence=0,
            ),
            cast.Credit(
                person_imdb_id="nm0000080",
                name="Orson Welles",
                roles=["Unicrom"],
                notes="(voice)",
                sequence=1,
            ),
        ],
        writers=[
            writers.Credit(
                person_imdb_id="nm0295357",
                name="Ron Friedman",
                notes="(written by)",
                group=0,
                sequence=0,
            )
        ],
    )

    movie = movies.fetch("tt0092106")

    assert imdb_http_mock.called_once_with("0092106")
    assert expected == movie
