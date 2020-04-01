from typing import Callable

from movielog.watchlist_titles_table import WatchlistTitle, WatchlistTitlesTable
from tests import typehints

test_titles = [
    WatchlistTitle(movie_imdb_id="movie_1", director_imdb_id="director_1"),
    WatchlistTitle(movie_imdb_id="movie_2", performer_imdb_id="performer_1"),
    WatchlistTitle(movie_imdb_id="movie_3", writer_imdb_id="writer_1"),
    WatchlistTitle(movie_imdb_id="movie_4", collection_name="collection_1"),
]


def test_inserts_titles(
    sql_connection: typehints.Connection,
    get_table_info: Callable[..., typehints.TableInfoType],
) -> None:
    expected = [
        (1, "movie_1", "director_1", None, None, None),
        (2, "movie_2", None, "performer_1", None, None),
        (3, "movie_3", None, None, "writer_1", None),
        (4, "movie_4", None, None, None, "collection_1"),
    ]

    WatchlistTitlesTable.recreate()
    WatchlistTitlesTable.insert_watchlist_titles(test_titles)
    rows = []
    for row in sql_connection.execute("SELECT * FROM 'watchlist_titles';").fetchall():
        rows.append(tuple(dict(row).values()))

    assert rows == expected


def test_adds_indexes(
    sql_connection: typehints.Connection,
    get_table_info: Callable[..., typehints.TableInfoType],
) -> None:
    index_columns = set(
        [
            "index_watchlist_titles_on_movie_imdb_id",
            "index_watchlist_titles_on_director_imdb_id",
            "index_watchlist_titles_on_performer_imdb_id",
            "index_watchlist_titles_on_writer_imdb_id",
        ]
    )

    WatchlistTitlesTable.recreate()
    WatchlistTitlesTable.insert_watchlist_titles(test_titles)
    rows = sql_connection.execute("PRAGMA index_list('watchlist_titles');").fetchall()
    for row in rows:
        assert row["name"] in index_columns
