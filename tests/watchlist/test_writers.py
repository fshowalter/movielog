import json
import os
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.watchlist import api as watchlist_api
from movielog.watchlist import serializer, writers
from movielog.watchlist.movies import Movie


@pytest.fixture(autouse=True)
def mock_movies_for_writer(mocker: MockerFixture) -> None:
    movies = [
        Movie(
            title="The Big Sleep",
            year=1946,
            imdb_id="tt0038355",
            notes=None,
        )
    ]
    mocker.patch(
        "movielog.watchlist.writers.movies_for_writer",
        MagicMock(return_value=movies),
    )


def test_add_writer_serializes_writer(
    tmp_path: str,
) -> None:
    expected = {
        "frozen": False,
        "name": "Leigh Brackett",
        "imdb_id": "nm0102824",
        "slug": "leigh-brackett",
        "movies": [
            {
                "title": "The Big Sleep",
                "year": 1946,
                "imdb_id": "tt0038355",
                "notes": None,
            }
        ],
    }

    watchlist_api.add_writer(imdb_id="nm0102824", name="Leigh Brackett")

    with open(
        os.path.join(tmp_path, "writers", "leigh-brackett.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_refresh_movies_adds_new_movies(
    tmp_path: str,
) -> None:
    expected = {
        "frozen": False,
        "name": "Leigh Brackett",
        "imdb_id": "nm0102824",
        "slug": "leigh-brackett",
        "movies": [
            {
                "title": "The Big Sleep",
                "year": 1946,
                "imdb_id": "tt0038355",
                "notes": None,
            }
        ],
    }

    serializer.serialize(
        writers.Writer(
            frozen=False,
            name="Leigh Brackett",
            slug="leigh-brackett",
            imdb_id="nm0102824",
            movies=[],
        )
    )

    writers.refresh_movies()

    with open(
        os.path.join(tmp_path, "writers", "leigh-brackett.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_refresh_movies_does_not_update_frozen_entries(
    tmp_path: str,
) -> None:
    expected = {
        "frozen": True,
        "name": "Leigh Brackett",
        "imdb_id": "nm0102824",
        "slug": "leigh-brackett",
        "movies": [],
    }

    serializer.serialize(
        writers.Writer(
            frozen=True,
            name="Leigh Brackett",
            slug="leigh-brackett",
            imdb_id="nm0102824",
            movies=[],
        )
    )

    writers.refresh_movies()

    with open(
        os.path.join(tmp_path, "writers", "leigh-brackett.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
