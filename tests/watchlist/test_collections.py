import json
import os

from movielog.watchlist import collections
from movielog.watchlist.movies import Movie


def test_add_serializes_new_collection(tmp_path: str) -> None:
    expected = {
        "name": "Halloween",
        "slug": "halloween",
        "movies": [],
    }

    collections.add(name="Halloween")

    with open(
        os.path.join(tmp_path, "collections", "halloween.json"), "r"
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == expected


def test_add_movie_adds_title() -> None:
    collection = collections.add(name="Hammer Films")

    expected = [
        Movie(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957)
    ]

    collection = collections.add_movie(
        collection=collection,
        imdb_id="tt0050280",
        title="The Curse of Frankenstein",
        year=1957,
    )

    assert collection.movies == expected


def test_add_movie_sorts_added_title_by_year() -> None:
    expected = [
        Movie(imdb_id="tt0050280", title="The Curse of Frankenstein", year=1957),
        Movie(imdb_id="tt0051554", title="Horror of Dracula", year=1958),
        Movie(imdb_id="tt0053085", title="The Mummy", year=1959),
    ]

    collection = collections.add(name="Hammer Films")

    collection = collections.add_movie(
        collection=collection,
        imdb_id="tt0050280",
        title="The Curse of Frankenstein",
        year=1957,
    )
    collection = collections.add_movie(
        collection=collection, imdb_id="tt0053085", title="The Mummy", year=1959
    )

    collection = collections.add_movie(
        collection=collection, imdb_id="tt0051554", title="Horror of Dracula", year=1958
    )

    assert collection.movies == expected


def test_deserialize_all_returns_all_collections() -> None:
    collection1 = collections.add(name="Friday the 13th")
    collection2 = collections.add(name="James Bond")

    expected = [
        collection1,
        collection2,
    ]

    assert collections.deserialize_all() == expected
