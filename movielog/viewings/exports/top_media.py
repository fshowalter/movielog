from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger

MAX_RESULTS = 10

MediumStats = TypedDict(
    "MediumStats",
    {
        "name": str,
        "viewingCount": int,
    },
)


StatGroup = TypedDict(
    "StatGroup",
    {
        "viewingYear": str,
        "totalViewingCount": int,
        "stats": list[MediumStats],
    },
)


class Row(TypedDict):
    viewing_year: str
    viewing_medium: str


def fetch_rows() -> list[Row]:
    query = """
        SELECT
        strftime('%Y', viewings.date) AS viewing_year
        , viewings.medium AS viewing_medium
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        WHERE viewing_medium IS NOT NULL
    """

    return db.fetch_all(query)


def medium_stats_for_rows(rows: list[Row]) -> list[MediumStats]:
    medium_stats: list[MediumStats] = []
    viewings_by_medium = list_tools.group_list_by_key(
        rows, lambda row: row["viewing_medium"]
    )

    for name, medium_viewings in viewings_by_medium.items():
        medium_stats.append(MediumStats(name=name, viewingCount=len(medium_viewings)))

    return sorted(medium_stats, reverse=True, key=lambda stat: stat["viewingCount"])[
        :MAX_RESULTS
    ]


def export() -> None:
    logger.log("==== Begin exporting {}...", "top venues")
    rows = fetch_rows()
    stat_groups = [
        StatGroup(
            viewingYear="all",
            totalViewingCount=len(rows),
            stats=medium_stats_for_rows(rows),
        )
    ]

    rows_by_year = list_tools.group_list_by_key(rows, lambda row: row["viewing_year"])
    for year, rows_for_year in rows_by_year.items():
        stat_groups.append(
            StatGroup(
                viewingYear=year,
                totalViewingCount=len(rows_for_year),
                stats=medium_stats_for_rows(rows_for_year),
            )
        )

    export_tools.serialize_dicts_to_folder(
        dicts=stat_groups,
        folder_name="top_media",
        filename_key=lambda stat_file: stat_file["viewingYear"],
    )
