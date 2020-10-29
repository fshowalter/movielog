from datetime import date
from unittest.mock import MagicMock

import imdb
import pytest
from pytest_mock import MockerFixture

from movielog import imdb_http


@pytest.fixture(autouse=True)
def imdb_scraper_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(
        imdb_http.imdb_scraper,
        "get_movie",
        return_value={
            "imdbID": "0092106",
            "title": "The Transformers: The Movie",
            "year": 1986,
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


def test_gets_cast_credits_for_title_from_imdb(
    imdb_scraper_mock: MagicMock,
) -> None:
    expected_title_info = imdb_http.TitleDetail(
        imdb_id="tt0092106",
        title="The Transformers: The Movie",
        year=1986,
        release_date=date(1986, 8, 8),
        release_date_notes="",
        directors=[
            imdb_http.DirectingCreditForTitle(
                movie_imdb_id="tt0092106",
                person_imdb_id="nm0793802",
                name="Nelson Shin",
                notes="",
                sequence=0,
            )
        ],
        writers=[
            imdb_http.WritingCreditForTitle(
                movie_imdb_id="tt0092106",
                person_imdb_id="nm0295357",
                name="Ron Friedman",
                notes="(written by)",
                group=0,
                sequence=0,
            )
        ],
        cast=[
            imdb_http.CastCreditForTitle(
                movie_imdb_id="tt0092106",
                person_imdb_id="nm0191520",
                name="Peter Cullen",
                roles=["Optimus Prime", "Ironhide"],
                notes="(voice)",
                sequence=0,
            ),
            imdb_http.CastCreditForTitle(
                movie_imdb_id="tt0092106",
                person_imdb_id="nm0000080",
                name="Orson Welles",
                roles=["Unicrom"],
                notes="(voice)",
                sequence=1,
            ),
        ],
    )

    title_info = imdb_http.info_for_title(title_imdb_id="tt0092106")

    assert imdb_scraper_mock.called_once_with("0092106")
    assert title_info == expected_title_info
