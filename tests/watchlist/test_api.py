import json
import os
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog.watchlist import api as watchlist_api
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
        "movielog.watchlist.directors.movies_for_director",
        MagicMock(return_value=movies),
    )


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


@pytest.fixture(autouse=True)
def mock_movies_for_performer(mocker: MockerFixture) -> None:
    movies = [
        Movie(
            title="Rio Bravo",
            year=1959,
            imdb_id="tt0053221",
            notes=None,
        )
    ]
    mocker.patch(
        "movielog.watchlist.performers.movies_for_performer",
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

    with open(os.path.join(tmp_path, "orson-welles.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


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

    with open(os.path.join(tmp_path, "leigh-brackett.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_add_performer_serializes_performer(
    tmp_path: str,
) -> None:
    expected = {
        "frozen": False,
        "name": "John Wayne",
        "imdb_id": "nm0000078",
        "slug": "john-wayne",
        "movies": [
            {
                "title": "Rio Bravo",
                "year": 1959,
                "imdb_id": "tt0053221",
                "notes": None,
            }
        ],
    }

    watchlist_api.add_performer(imdb_id="nm0000078", name="John Wayne")

    with open(os.path.join(tmp_path, "john-wayne.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_add_collection_serializes_new_collection(tmp_path: str) -> None:
    expected = {
        "name": "Halloween",
        "slug": "halloween",
        "movies": [],
    }

    watchlist_api.add_collection(name="Halloween")

    with open(os.path.join(tmp_path, "halloween.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_add_movie_to_collection_adds_title() -> None:
    collection = watchlist_api.add_collection(name="Hammer Films")

    expected = [
        Movie(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957)
    ]

    collection = watchlist_api.add_movie_to_collection(
        collection=collection,
        imdb_id="tt0050280",
        title="The Curse of Frankenstein",
        year=1957,
    )

    assert collection.movies == expected


def test_add_movie_to_collection_sorts_added_title_by_year() -> None:
    expected = [
        Movie(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957),
        Movie(imdb_id="tt0051554", title="Horror of Dracula", year=1958),
        Movie(imdb_id="tt0053085", title="The Mummy", year=1959),
    ]

    collection = watchlist_api.add_collection(name="Hammer Films")

    collection = watchlist_api.add_movie_to_collection(
        collection=collection,
        imdb_id="tt0050280",
        title="The Curse of Frankenstein",
        year=1957,
    )
    collection = watchlist_api.add_movie_to_collection(
        collection=collection, imdb_id="tt0053085", title="The Mummy", year=1959
    )

    collection = watchlist_api.add_movie_to_collection(
        collection=collection, imdb_id="tt0051554", title="Horror of Dracula", year=1958
    )

    assert collection.movies == expected


def test_collections_returns_all_collections() -> None:
    collection1 = watchlist_api.add_collection(name="Friday the 13th")
    collection2 = watchlist_api.add_collection(name="James Bond")

    expected = [
        collection1,
        collection2,
    ]

    assert watchlist_api.collections() == expected
