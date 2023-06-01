from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger

LIMIT = 10


Movie = TypedDict(
    "Movie",
    {
        "viewingCount": int,
        "imdbId": str,
        "title": str,
        "year": str,
    },
)

StatGroup = TypedDict(
    "StatGroup",
    {
        "viewingYear": str,
        "mostWatched": list[Movie],
    },
)


class Row(TypedDict):
    movie_title: str
    movie_year: str
    movie_imdb_id: str
    viewing_year: str


def fetch_rows() -> list[Row]:
    query = """
        SELECT
        movies.title AS movie_title
        , movies.year AS movie_year
        , movies.imdb_id AS movie_imdb_id
        , strftime('%Y', viewings.date) AS viewing_year
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        ORDER BY
            viewing_year
    """

    return db.fetch_all(query)


def most_watched_movies_for_rows(rows: list[Row]) -> list[Movie]:
    most_watched_movies: list[Movie] = []
    rows_by_movie_imdb_id = list_tools.group_list_by_key(
        rows, lambda row: row["movie_imdb_id"]
    )

    for movie_imdb_id_rows in rows_by_movie_imdb_id.values():
        if len(movie_imdb_id_rows) == 1:
            continue
        first_row = movie_imdb_id_rows[0]
        most_watched_movies.append(
            Movie(
                imdbId=first_row["movie_imdb_id"],
                title=first_row["movie_title"],
                year=first_row["movie_year"],
                viewingCount=len(movie_imdb_id_rows),
            )
        )

    return sorted(
        most_watched_movies, reverse=True, key=lambda movie: movie["viewingCount"]
    )[:LIMIT]


def export() -> None:
    logger.log("==== Begin exporting {}...", "most watched movies")

    rows = fetch_rows()
    rows_by_viewing_year = list_tools.group_list_by_key(
        rows, lambda row: row["viewing_year"]
    )
    stat_files = [
        StatGroup(viewingYear="all", mostWatched=most_watched_movies_for_rows(rows))
    ]

    for year, rows_for_year in rows_by_viewing_year.items():
        stat_files.append(
            StatGroup(
                viewingYear=year,
                mostWatched=most_watched_movies_for_rows(rows_for_year),
            ),
        )

    export_tools.serialize_dicts_to_folder(
        dicts=stat_files,
        folder_name="most_watched_movies",
        filename_key=lambda stats: stats["viewingYear"],
    )
