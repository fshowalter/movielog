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
            "title": "The Transformers: The Movie",
            "year": 1986,
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
                imdb.Person.Person(
                    personID="1084210",
                    name="Simon Furman",
                    notes="",
                    currentRole="",
                ),
            ],
        },
    )


def test_gets_cast_credits_for_title_from_imdb(
    imdb_scraper_mock: MagicMock,
) -> None:
    expected_title_basic = imdb_http.TitleBasic(
        imdb_id="tt0092106",
        title="The Transformers: The Movie",
        year=1986,
    )

    expected_cast_credits = [
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
        imdb_http.CastCreditForTitle(
            movie_imdb_id="tt0092106",
            person_imdb_id="nm1084210",
            name="Simon Furman",
            roles=[],
            notes="",
            sequence=2,
        ),
    ]

    title_basic, cast_credits = imdb_http.cast_credits_for_title(
        title_imdb_id="tt0092106"
    )

    assert imdb_scraper_mock.called_once_with("0092106")
    assert title_basic == expected_title_basic
    assert cast_credits == expected_cast_credits
