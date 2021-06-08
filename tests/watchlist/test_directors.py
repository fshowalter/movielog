import json
import os
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.watchlist import api as watchlist_api
from movielog.watchlist import directors, serializer
from movielog.watchlist.movies import Movie


@pytest.fixture(autouse=True)
def mock_movies_for_director(mocker: MockerFixture) -> None:
    movies = [
        Movie(
            title="Citizen Kane",
            year=1941,
            imdb_id="tt0033467",
            notes=None,
        )
    ]
    mocker.patch(
        "movielog.watchlist.directors.filmography.for_director",
        MagicMock(return_value=movies),
    )


def test_add_director_serializes_director(
    tmp_path: str,
) -> None:
    expected = {
        "frozen": False,
        "name": "Orson Welles",
        "imdb_id": "nm0000080",
        "slug": "orson-welles",
        "movies": [
            {
                "title": "Citizen Kane",
                "year": 1941,
                "imdb_id": "tt0033467",
                "notes": None,
            }
        ],
    }

    watchlist_api.add_director(imdb_id="nm0000080", name="Orson Welles")

    with open(
        os.path.join(tmp_path, "directors", "orson-welles.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_refresh_movies_adds_new_movies(tmp_path: str) -> None:
    expected = {
        "frozen": False,
        "name": "Orson Welles",
        "imdb_id": "nm0000080",
        "slug": "orson-welles",
        "movies": [
            {
                "title": "Citizen Kane",
                "year": 1941,
                "imdb_id": "tt0033467",
                "notes": None,
            }
        ],
    }

    serializer.serialize(
        directors.Director(
            frozen=False,
            name="Orson Welles",
            imdb_id="nm0000080",
            slug="orson-welles",
            movies=[],
        )
    )

    directors.refresh_movies()

    with open(
        os.path.join(tmp_path, "directors", "orson-welles.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_refresh_does_not_update_frozen_entries(tmp_path: str) -> None:
    expected = {
        "frozen": True,
        "name": "Orson Welles",
        "imdb_id": "nm0000080",
        "slug": "orson-welles",
        "movies": [],
    }

    serializer.serialize(
        directors.Director(
            frozen=True,
            name="Orson Welles",
            imdb_id="nm0000080",
            slug="orson-welles",
            movies=[],
        )
    )

    directors.refresh_movies()

    with open(
        os.path.join(tmp_path, "directors", "orson-welles.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
