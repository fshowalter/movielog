from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger


@dataclass
class VenueStat(object):
    venue: str
    viewing_count: int


@dataclass
class StatFile(object):
    viewing_year: str
    total_viewing_count: int
    venue_stats: list[VenueStat]


class Row(TypedDict):
    viewing_year: str
    viewing_venue: str


def fetch_rows() -> list[Row]:
    query = """
        SELECT
        strftime('%Y', viewings.date) AS viewing_year
        , viewings.venue
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
    """

    return db.fetch_all(query)


def venue_stats_for_rows(rows: list[Row]) -> list[VenueStat]:
    venue_stats: list[VenueStat] = []
    viewings_by_venue = list_tools.group_list_by_key(
        rows, lambda row: row["viewing_venue"]
    )

    for venue, venue_viewings in viewings_by_venue.items():
        venue_stats.append(VenueStat(venue=venue, viewing_count=len(venue_viewings)))

    return sorted(venue_stats, key=lambda stat: stat.venue.lower())


def export() -> None:
    logger.log("==== Begin exporting {}...", "viewings counts for venues")
    rows = fetch_rows()
    stat_files = [
        StatFile(
            viewing_year="all",
            total_viewing_count=len(rows),
            venue_stats=venue_stats_for_rows(rows),
        )
    ]

    rows_by_year = list_tools.group_list_by_key(rows, lambda row: row["viewing_year"])
    for year, rows_for_year in rows_by_year.items():
        stat_files.append(
            StatFile(
                viewing_year=year,
                total_viewing_count=len(rows_for_year),
                venue_stats=venue_stats_for_rows(rows_for_year),
            )
        )

    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="viewing_counts_for_venues",
        filename_key=lambda stat_file: stat_file.viewing_year,
    )
