from typing import Callable

from movielog.watchlist import movies, table_updater
from movielog.watchlist.collections import Collection
from movielog.watchlist.directors import Director
from movielog.watchlist.performers import Performer
from movielog.watchlist.writers import Writer
from tests.conftest import QueryResult


def test_update_reloads_watchlist_table_with_given_entities(
    sql_query: Callable[[str], QueryResult]
) -> None:

    people = [
        Director(
            frozen=True,
            imdb_id="nm0001328",
            name="Howard Hawks",
            slug="howard-hawks",
            movies=[
                movies.Movie(
                    title="Rio Bravo", year=1959, imdb_id="tt0053221", notes=""
                )
            ],
        ),
        Performer(
            frozen=True,
            imdb_id="nm0000078",
            name="John Wayne",
            slug="john-wayne",
            movies=[
                movies.Movie(
                    title="Rio Bravo", year=1959, imdb_id="tt0053221", notes=""
                )
            ],
        ),
        Writer(
            frozen=True,
            imdb_id="nm0102824",
            name="Leigh Brackett",
            slug="leigh-brackett",
            movies=[
                movies.Movie(
                    imdb_id="tt0038355", title="The Big Sleep", year=1946, notes=""
                )
            ],
        ),
    ]

    collections = [
        Collection(
            name="Vampire Movies",
            slug="vampire-movies",
            movies=[
                movies.Movie(
                    imdb_id="tt0089175",
                    title="Fright Night",
                    year=1985,
                    notes="",
                )
            ],
        )
    ]

    expected = [
        {
            "id": 1,
            "movie_imdb_id": "tt0053221",
            "director_imdb_id": "nm0001328",
            "performer_imdb_id": None,
            "writer_imdb_id": None,
            "collection_name": None,
            "slug": "howard-hawks",
        },
        {
            "id": 2,
            "movie_imdb_id": "tt0053221",
            "director_imdb_id": None,
            "performer_imdb_id": "nm0000078",
            "writer_imdb_id": None,
            "collection_name": None,
            "slug": "john-wayne",
        },
        {
            "id": 3,
            "movie_imdb_id": "tt0038355",
            "director_imdb_id": None,
            "performer_imdb_id": None,
            "writer_imdb_id": "nm0102824",
            "collection_name": None,
            "slug": "leigh-brackett",
        },
        {
            "id": 4,
            "movie_imdb_id": "tt0089175",
            "director_imdb_id": None,
            "performer_imdb_id": None,
            "writer_imdb_id": None,
            "collection_name": "Vampire Movies",
            "slug": "vampire-movies",
        },
    ]

    table_updater.update(people, collections)

    assert expected == sql_query("SELECT * FROM 'watchlist' order by id;")
