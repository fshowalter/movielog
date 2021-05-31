from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger


@dataclass
class Viewing(object):
    date: date
    venue: str
    sequence: int


@dataclass
class Movie(object):
    viewings: list[Viewing]
    viewing_count: int
    imdb_id: str
    title: str
    year: str
    slug: str


@dataclass
class StatFile(object):
    viewing_year: str
    movies: list[Movie]


class Row(TypedDict):
    viewing_sequence: int
    movie_title: str
    movie_year: str
    movie_imdb_id: str
    movie_slug: str
    viewing_year: str
    viewing_date: date
    viewing_venue: str


def fetch_rows() -> list[Row]:
    query = """
        SELECT
            viewings.sequence AS viewing_sequence
        , movies.title AS movie_title
        , movies.year AS movie_year
        , movies.imdb_id AS movie_imdb_id
        , slug AS movie_slug
        , strftime('%Y', viewings.date) AS viewing_year
        , viewings.date AS viewing_date
        , viewings.venue AS viewing_venue
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        LEFT JOIN reviews ON reviews.movie_imdb_id = movies.imdb_id
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
                imdb_id=first_row["movie_imdb_id"],
                title=first_row["movie_title"],
                slug=first_row["movie_slug"],
                year=first_row["movie_year"],
                viewing_count=len(movie_imdb_id_rows),
                viewings=[
                    Viewing(
                        sequence=row["viewing_sequence"],
                        date=row["viewing_date"],
                        venue=row["viewing_venue"],
                    )
                    for row in movie_imdb_id_rows
                ],
            )
        )

    return sorted(
        most_watched_movies, reverse=True, key=lambda movie: len(movie.viewings)
    )


def export() -> None:
    logger.log("==== Begin exporting {}...", "most watched movies")

    rows = fetch_rows()
    rows_by_viewing_year = list_tools.group_list_by_key(
        rows, lambda row: row["viewing_year"]
    )
    stat_files = [
        StatFile(viewing_year="all", movies=most_watched_movies_for_rows(rows))
    ]

    for year, rows_for_year in rows_by_viewing_year.items():
        stat_files.append(
            StatFile(
                viewing_year=year,
                movies=most_watched_movies_for_rows(rows_for_year),
            ),
        )

    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="most_watched_movies",
        filename_key=lambda stats: stats.viewing_year,
    )
