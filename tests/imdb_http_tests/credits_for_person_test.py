from typing import Any

import imdb
import pytest
from pytest_mock import MockFixture

from movielog import imdb_http


@pytest.fixture(autouse=True)
def imdb_scraper_mock(mocker: MockFixture) -> Any:
    actor_movie = imdb.Movie.Movie(
        movieID="0092106",
        title="The Transformers: The Movie (1986)",
        notes="",
        status=None,
    )
    director_movie = imdb.Movie.Movie(
        movieID="0052311", title="Touch of Evil (1958)", notes="", status=None,
    )
    writer_movie = imdb.Movie.Movie(
        movieID="0035015",
        title="The Magnificent Ambersons (1942)",
        notes="",
        status=None,
    )
    return mocker.patch.object(
        imdb_http.imdb_scraper,
        "get_person",
        return_value={
            "filmography": [
                {"actor": [actor_movie]},
                {"director": [director_movie]},
                {"writer": [writer_movie]},
            ]
        },
    )


def test_gets_performer_credits_for_person_from_imdb(
    imdb_scraper_mock: MockFixture,
) -> None:
    expected = [
        imdb_http.CreditForPerson(
            imdb_id="tt0092106",
            title="The Transformers: The Movie",
            year=1986,
            notes="",
            in_production=None,
        )
    ]

    credits_for_person = imdb_http.credits_for_person(
        person_imdb_id="nm0000080", credit_key="performer"
    )

    assert imdb_scraper_mock.called_once_with("nm0000080", "performer")
    assert credits_for_person == expected


def test_gets_director_credits_for_person_from_imdb(
    imdb_scraper_mock: MockFixture,
) -> None:
    expected = [
        imdb_http.CreditForPerson(
            imdb_id="tt0052311",
            title="Touch of Evil",
            year=1958,
            notes="",
            in_production=None,
        )
    ]

    credits_for_person = imdb_http.credits_for_person(
        person_imdb_id="nm0000080", credit_key="director"
    )

    assert imdb_scraper_mock.called_once_with("nm0000080", "director")
    assert credits_for_person == expected


def test_gets_writer_credits_for_person_from_imdb(
    imdb_scraper_mock: MockFixture,
) -> None:
    expected = [
        imdb_http.CreditForPerson(
            imdb_id="tt0035015",
            title="The Magnificent Ambersons",
            year=1942,
            notes="",
            in_production=None,
        )
    ]

    credits_for_person = imdb_http.credits_for_person(
        person_imdb_id="nm0000080", credit_key="writer"
    )

    assert imdb_scraper_mock.called_once_with("nm0000080", "writer")
    assert credits_for_person == expected
