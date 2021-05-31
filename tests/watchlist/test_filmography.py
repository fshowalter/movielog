from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from unittest.mock import MagicMock

import imdb
import pytest
from pytest_mock import MockerFixture

from movielog.watchlist import filmography


@pytest.fixture
def imdb_movie() -> imdb.Movie.Movie:
    return imdb.Movie.Movie(
        movieID="0092106",
        title="The Transformers: The Movie",
    )


@pytest.fixture(autouse=True)
def imdb_http_mock(mocker: MockerFixture) -> MagicMock:
    mocker.patch.object(
        filmography.imdb_http, "get_movie", return_value=imdb.Movie.Movie()
    )
    return mocker.patch.object(
        filmography.imdb_http,
        "update",
    )


@pytest.fixture(autouse=True)
def reset_cache() -> None:
    filmography.silent_ids = set()
    filmography.no_sound_mix_ids = set()


def test_is_silent_returns_none_if_no_sound_mix(
    imdb_http_mock: MagicMock, imdb_movie: imdb.Movie.Movie
) -> None:
    def factory(movie: imdb.Movie.Movie, info: list[str]) -> None:  # noqa: WPS110
        movie["tech"] = {}

    imdb_http_mock.side_effect = factory

    assert filmography.is_silent(imdb_movie) is None
    assert "0092106" in filmography.no_sound_mix_ids
    assert "0092106" not in filmography.silent_ids


def test_is_silent_returns_true_if_sound_mix_and_silent(
    imdb_http_mock: MagicMock, imdb_movie: imdb.Movie.Movie
) -> None:
    def factory(movie: imdb.Movie.Movie, info: list[str]) -> None:  # noqa: WPS110
        movie["tech"] = {"sound mix": ["Silent"]}

    imdb_http_mock.side_effect = factory

    assert filmography.is_silent(imdb_movie) is True
    assert "0092106" not in filmography.no_sound_mix_ids
    assert "0092106" in filmography.silent_ids


def test_is_silent_returns_false_if_sound_mix_and_not_silent(
    imdb_http_mock: MagicMock, imdb_movie: imdb.Movie.Movie
) -> None:
    def factory(movie: imdb.Movie.Movie, info: list[str]) -> None:  # noqa: WPS110
        movie["tech"] = {"sound mix": ["Dolby"]}

    imdb_http_mock.side_effect = factory

    assert filmography.is_silent(imdb_movie) is False
    assert "0092106" not in filmography.no_sound_mix_ids
    assert "0092106" not in filmography.silent_ids


def test_is_silent_returns_true_if_in_silent_ids_cache(
    imdb_movie: imdb.Movie.Movie,
) -> None:
    filmography.silent_ids = set(["0092106"])

    assert filmography.is_silent(imdb_movie) is True


def test_is_silent_returns_none_if_not_in_silent_ids_in_no_sound_mix_ids_cache(
    imdb_movie: imdb.Movie.Movie,
) -> None:
    filmography.no_sound_mix_ids = set(["0092106"])

    assert filmography.is_silent(imdb_movie) is None


@pytest.mark.parametrize(
    "key",
    ["director", "performer", "writer"],
)
def test_valid_movies_for_person_filters_in_production_titles(
    mocker: MockerFixture, key: str
) -> None:
    expected = [
        {
            "imdb_id": "tt0017075",
            "title": "The Lodger: A Story of the London Fog",
            "year": 1927,
            "notes": "",
            "status": "",
        },
        {
            "imdb_id": "tt0053125",
            "title": "North by Northwest",
            "year": 1959,
            "notes": "",
            "status": None,
        },
    ]

    person = {
        "name": "Cary Grant",
        "filmography": {
            ("actor" if key == "performer" else key): [
                {
                    "imdb_id": "tt9999999",
                    "title": "North by Northwest 2",
                    "year": 2025,
                    "notes": "based on",
                    "status": "In Production",
                },
                {
                    "imdb_id": "tt0053125",
                    "title": "North by Northwest",
                    "year": 1959,
                    "notes": "",
                    "status": None,
                },
                {
                    "imdb_id": "tt0017075",
                    "title": "The Lodger: A Story of the London Fog",
                    "year": 1927,
                    "notes": "",
                    "status": "",
                },
            ],
        },
    }

    mocker.patch(
        "movielog.watchlist.filmography.imdb_http.get_person",
        return_value=person,
    )

    mocker.patch(
        "movielog.watchlist.filmography.has_invalid_movie_id", return_value=False
    )

    mocker.patch("movielog.watchlist.filmography.is_silent", return_value=False)

    movies = [
        movie
        for _person, movie in filmography.valid_movies_for_person(
            person_imdb_id="any", key=key
        )
    ]

    assert movies == expected


@pytest.mark.parametrize(
    "key",
    ["director", "performer", "writer"],
)
def test_valid_movies_for_person_filters_in_silent_titles(
    mocker: MockerFixture, key: str
) -> None:
    expected = [
        {
            "imdb_id": "tt0053125",
            "title": "North by Northwest",
            "year": 1959,
            "notes": "",
            "status": None,
        },
        {
            "imdb_id": "tt9999999",
            "title": "North by Northwest 2",
            "year": 2025,
            "notes": "based on",
            "status": "",
        },
    ]

    person = {
        "name": "Cary Grant",
        "filmography": {
            ("actor" if key == "performer" else key): [
                {
                    "imdb_id": "tt9999999",
                    "title": "North by Northwest 2",
                    "year": 2025,
                    "notes": "based on",
                    "status": "",
                },
                {
                    "imdb_id": "tt0053125",
                    "title": "North by Northwest",
                    "year": 1959,
                    "notes": "",
                    "status": None,
                },
                {
                    "imdb_id": "tt0017075",
                    "title": "The Lodger: A Story of the London Fog",
                    "year": 1927,
                    "notes": "",
                    "status": "",
                },
            ],
        },
    }

    mocker.patch(
        "movielog.watchlist.filmography.imdb_http.get_person",
        return_value=person,
    )

    mocker.patch(
        "movielog.watchlist.filmography.has_invalid_movie_id", return_value=False
    )

    is_silent_mock = mocker.patch(
        "movielog.watchlist.filmography.is_silent", return_value=False
    )

    def factory(movie: imdb.Movie.Movie) -> bool:
        return bool(movie["imdb_id"] == "tt0017075")

    is_silent_mock.side_effect = factory

    assert expected == [
        movie
        for _person, movie in filmography.valid_movies_for_person(
            person_imdb_id="any", key=key
        )
    ]


@dataclass
class MockMovie(object):
    movieID: str  # noqa: WPS115, N815
    title: str
    year: int
    notes: str
    status: Optional[str]


@pytest.mark.parametrize(
    "key",
    ["director", "performer", "writer"],
)
def test_valid_movies_for_person_filters_invalid_title_ids(
    mocker: MockerFixture, key: str
) -> None:
    expected = [
        imdb.Movie.Movie(
            movieID="0017075",
            title="The Lodger: A Story of the London Fog",
            year=1927,
            notes="",
            status="",
        ),
    ]

    person = {
        "name": "Cary Grant",
        "filmography": {
            ("actor" if key == "performer" else key): [
                imdb.Movie.Movie(
                    movieID="9999999",
                    title="North by Northwest 2",
                    year=2025,
                    notes="based on",
                    status="",
                ),
                imdb.Movie.Movie(
                    movieID="0053125",
                    title="North by Northwest",
                    year=1959,
                    notes="",
                    status=None,
                ),
                imdb.Movie.Movie(
                    movieID="0017075",
                    title="The Lodger: A Story of the London Fog",
                    year=1927,
                    notes="",
                    status="",
                ),
            ],
        },
    }

    mocker.patch(
        "movielog.watchlist.filmography.imdb_http.get_person",
        return_value=person,
    )

    mocker.patch(
        "movielog.watchlist.filmography.moviedata_api.movie_ids",
        return_value=set(["tt0017075"]),
    )

    mocker.patch("movielog.watchlist.filmography.is_silent", return_value=False)

    assert expected == [
        movie
        for _person, movie in filmography.valid_movies_for_person(
            person_imdb_id="any", key=key
        )
    ]
