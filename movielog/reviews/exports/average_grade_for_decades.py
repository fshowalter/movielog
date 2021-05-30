from dataclasses import dataclass
from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger


@dataclass
class DecadeStat(object):
    decade: str
    average_grade_value: float


class Row(TypedDict):
    review_year: str
    grade_value: int
    movie_decade: str


@dataclass
class StatFile(object):
    review_year: str
    decade_stats: list[DecadeStat]


def fetch_rows() -> list[Row]:
    query = """
        SELECT
        reviews.sequence
        , grade_value
        , strftime('%Y', reviews.date) AS review_year
        , substr(movies.year, 1, 3) || '0s' AS movie_decade
        FROM reviews
        LEFT JOIN movies ON movies.imdb_id = reviews.movie_imdb_id
    """

    return db.fetch_all(query)


def decade_stats_for_rows(rows: list[Row]) -> list[DecadeStat]:
    decades: list[DecadeStat] = []
    rows_by_decade = list_tools.group_list_by_key(rows, lambda row: row["movie_decade"])

    for decade, decade_rows in rows_by_decade.items():
        decades.append(
            DecadeStat(
                decade=decade,
                average_grade_value=sum(
                    decade_row["grade_value"] for decade_row in decade_rows
                )
                / len(decade_rows),
            )
        )

    return sorted(decades, key=lambda group: group.decade)


def export() -> None:
    logger.log("==== Begin exporting {}...", "average grade for decades")
    rows = fetch_rows()
    stat_files = [StatFile(review_year="all", decade_stats=decade_stats_for_rows(rows))]

    rows_by_year = list_tools.group_list_by_key(rows, lambda row: row["review_year"])
    for year, rows_for_year in rows_by_year.items():
        stat_files.append(
            StatFile(
                review_year=str(year),
                decade_stats=decade_stats_for_rows(rows_for_year),
            )
        )

    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="average_grade_for_decades",
        filename_key=lambda stat_file: stat_file.review_year,
    )
