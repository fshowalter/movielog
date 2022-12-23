from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger

DecadeStat = TypedDict(
    "DecadeStat",
    {
        "decade": str,
        "viewingCount": int,
    },
)


StatFile = TypedDict(
    "StatFile",
    {
        "viewingYear": str,
        "totalViewingCount": int,
        "stats": list[DecadeStat],
    },
)


class Row(TypedDict):
    viewing_year: str
    movie_decade: str


def fetch_rows() -> list[Row]:
    query = """
        SELECT
        strftime('%Y', viewings.date) AS viewing_year
        , substr(movies.year, 1, 3) || '0s' AS movie_decade
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
    """

    return db.fetch_all(query)


def decade_stats_for_rows(rows: list[Row]) -> list[DecadeStat]:
    decades: list[DecadeStat] = []
    viewings_by_decade = list_tools.group_list_by_key(
        rows, lambda row: row["movie_decade"]
    )

    for decade, decade_rows in viewings_by_decade.items():
        decades.append(DecadeStat(decade=decade, viewingCount=len(decade_rows)))

    return sorted(decades, key=lambda group: group["decade"])


def export() -> None:
    logger.log("==== Begin exporting {}...", "viewing counts for decades")
    rows = fetch_rows()
    stat_files = [
        StatFile(
            viewingYear="all",
            totalViewingCount=len(rows),
            stats=decade_stats_for_rows(rows),
        )
    ]

    rows_by_year = list_tools.group_list_by_key(rows, lambda row: row["viewing_year"])
    for year, rows_for_year in rows_by_year.items():
        stat_files.append(
            StatFile(
                viewingYear=year,
                totalViewingCount=len(rows_for_year),
                stats=decade_stats_for_rows(rows_for_year),
            )
        )

    export_tools.serialize_dicts_to_folder(
        dicts=stat_files,
        folder_name="viewing_counts_for_decades",
        filename_key=lambda stat_file: stat_file["viewingYear"],
    )
