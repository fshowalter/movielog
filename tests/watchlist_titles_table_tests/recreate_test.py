from typing import Callable

from movielog.watchlist_titles_table import WatchlistTitlesTable
from tests import typehints

expected_schema = [
    # format: id|name|type|not_null|default|is_pk # noqa: E800
    (0, "id", "INTEGER", 1, None, 1),
    (1, "movie_imdb_id", "TEXT", 1, None, 0),
    (2, "director_imdb_id", "TEXT", 0, None, 0),
    (3, "performer_imdb_id", "TEXT", 0, None, 0),
    (4, "writer_imdb_id", "TEXT", 0, None, 0),
    (5, "collection_name", "TEXT", 0, None, 0),
]


def test_creates_table(get_table_info: Callable[..., typehints.TableInfoType]) -> None:
    WatchlistTitlesTable.recreate()

    table_info = get_table_info("watchlist_titles")

    assert table_info == expected_schema


def test_recreates_table_if_exists(
    sql_connection: typehints.Connection,
    get_table_info: Callable[..., typehints.TableInfoType],
) -> None:
    sql_connection.execute(
        """
        CREATE TABLE "watchlist_titles" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "test_1" TEXT NOT NULL,
            "test_2" TEXT,
            "test_3" TEXT,
            "test_4" TEXT);
        """
    )  # noqa: WPS355

    WatchlistTitlesTable.recreate()

    table_info = get_table_info("watchlist_titles")

    assert table_info == expected_schema
