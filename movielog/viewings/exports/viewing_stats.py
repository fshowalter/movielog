from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger


class Row(TypedDict):
    viewing_year: str
    movie_imdb_id: str


StatGroup = TypedDict(
    "StatGroup",
    {
        "viewingYear": str,
        "movieCount": int,
        "newMovieCount": int,
        "viewingCount": int,
    },
)


def fetch_rows() -> list[Row]:
    query = """
        SELECT
            viewings.sequence
        , movies.imdb_id AS movie_imdb_id
        , strftime('%Y', viewings.date) AS viewing_year
        , viewings.date
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        ORDER BY
            viewing_year
    """

    return db.fetch_all(query)


def stats_for_rows_and_year(rows: list[Row], year: str) -> StatGroup:
    rows_for_year = list(filter(lambda row: row["viewing_year"] == year, rows))
    older_rows = list(filter(lambda row: row["viewing_year"] < year, rows))
    movie_ids_for_year = set(row["movie_imdb_id"] for row in rows_for_year)
    older_movie_ids = set(row["movie_imdb_id"] for row in older_rows)

    return StatGroup(
        viewingYear=year,
        movieCount=len(movie_ids_for_year),
        newMovieCount=len(movie_ids_for_year - older_movie_ids),
        viewingCount=len(rows_for_year),
    )


def build_all_stats_group(rows: list[Row]) -> list[StatGroup]:
    all_movie_ids = set(row["movie_imdb_id"] for row in rows)
    movie_count = len(all_movie_ids)
    return [
        StatGroup(
            viewingYear="all",
            movieCount=movie_count,
            newMovieCount=movie_count,
            viewingCount=len(rows),
        )
    ]


def export() -> None:
    logger.log("==== Begin exporting {}...", "viewing stats")
    rows = fetch_rows()
    stat_groups = build_all_stats_group(rows=rows)

    years = set(row["viewing_year"] for row in rows)
    for year in years:
        stat_groups.append(stats_for_rows_and_year(rows, year))

    export_tools.serialize_dicts_to_folder(
        dicts=stat_groups,
        folder_name="viewing_stats",
        filename_key=lambda stat_file: stat_file["viewingYear"],
    )
