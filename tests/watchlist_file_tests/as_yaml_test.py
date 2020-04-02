from typing import Callable

from movielog.watchlist_file import Title, WatchlistFile


def test_returns_as_object(build_watchlist_file: Callable[..., WatchlistFile]) -> None:
    expected = {
        "frozen": True,
        "name": "Hammer Films",
        "titles": [
            {
                "imdb_id": "tt0050280",
                "title": "The Curse of Frankenstein",
                "year": 1957,
            },
            {"imdb_id": "tt0051554", "title": "Horror of Dracula", "year": 1958},
        ],
    }

    titles = [
        Title(imdb_id="tt0050280", year=1957, title="The Curse of Frankenstein"),
        Title(imdb_id="tt0051554", year=1958, title="Horror of Dracula"),
    ]

    watchlist_file = build_watchlist_file(
        name="Hammer Films", frozen=True, titles=titles
    )

    assert watchlist_file.as_yaml() == expected


def test_if_imdb_id_adds_imdb_id(
    build_watchlist_file: Callable[..., WatchlistFile]
) -> None:
    expected = {
        "frozen": True,
        "name": "Peter Cushing",
        "imdb_id": "nm0001088",
        "titles": [
            {
                "imdb_id": "tt0050280",
                "title": "The Curse of Frankenstein",
                "year": 1957,
            },
            {"imdb_id": "tt0051554", "title": "Horror of Dracula", "year": 1958},
        ],
    }

    titles = [
        Title(imdb_id="tt0050280", year=1957, title="The Curse of Frankenstein"),
        Title(imdb_id="tt0051554", year=1958, title="Horror of Dracula"),
    ]

    watchlist_file = build_watchlist_file(
        name="Peter Cushing", frozen=True, titles=titles, imdb_id="nm0001088"
    )

    assert watchlist_file.as_yaml() == expected
