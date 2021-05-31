from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger


class Row(TypedDict):
    viewing_year: str
    movie_imdb_id: str


@dataclass
class StatFile(object):
    viewing_year: str
    movie_count: int
    new_movie_count: int
    viewing_count: int


def fetch_rows() -> list[Row]:
    query = """
        SELECT
            viewings.sequence
        , movies.imdb_id AS movie_imdb_id
        , strftime('%Y', viewings.date) AS viewing_year
        , viewings.date
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        LEFT JOIN reviews ON reviews.movie_imdb_id = movies.imdb_id
        ORDER BY
            viewing_year
    """

    return db.fetch_all(query)


def stats_for_rows_and_year(rows: list[Row], year: str) -> StatFile:
    rows_for_year = list(filter(lambda row: row["viewing_year"] == year, rows))
    older_rows = list(filter(lambda row: row["viewing_year"] < year, rows))
    movie_ids_for_year = set(row["movie_imdb_id"] for row in rows_for_year)
    older_movie_ids = set(row["movie_imdb_id"] for row in older_rows)

    return StatFile(
        viewing_year=year,
        movie_count=len(movie_ids_for_year),
        new_movie_count=len(movie_ids_for_year - older_movie_ids),
        viewing_count=len(rows_for_year),
    )


def export() -> None:
    logger.log("==== Begin exporting {}...", "viewing stats")
    rows = fetch_rows()
    movie_count = len(set(row["movie_imdb_id"] for row in rows))
    stat_files = [
        StatFile(
            viewing_year="all",
            movie_count=movie_count,
            new_movie_count=movie_count,
            viewing_count=len(rows),
        )
    ]

    years = set(row["viewing_year"] for row in rows)
    for year in years:
        stat_files.append(stats_for_rows_and_year(rows, year))

    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="viewing_stats",
        filename_key=lambda stat_file: stat_file.viewing_year,
    )
