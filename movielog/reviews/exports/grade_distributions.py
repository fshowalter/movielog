from dataclasses import dataclass
from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger


@dataclass
class Distribution(object):
    grade: str
    grade_value: float
    review_count: int


class Row(TypedDict):
    review_year: str
    grade_value: float
    grade: str


@dataclass
class StatFile(object):
    review_year: str
    total_review_count: int
    distributions: list[Distribution]


def fetch_rows() -> list[Row]:
    query = """
        SELECT
        grade
        , grade_value
        , strftime('%Y', reviews.date) AS review_year
        FROM reviews
    """

    return db.fetch_all(query)


def distribution_for_rows(rows: list[Row]) -> list[Distribution]:
    distributions: list[Distribution] = []
    rows_by_grade = list_tools.group_list_by_key(rows, lambda row: row["grade"])

    for grade, grade_rows in rows_by_grade.items():
        first_row = grade_rows[0]
        distributions.append(
            Distribution(
                grade=grade,
                grade_value=first_row["grade_value"],
                review_count=len(grade_rows),
            )
        )

    return sorted(distributions, reverse=True, key=lambda group: group.grade_value)


def export() -> None:
    logger.log("==== Begin exporting {}...", "grade distributions")
    rows = fetch_rows()
    stat_files = [
        StatFile(
            review_year="all",
            total_review_count=len(rows),
            distributions=distribution_for_rows(rows),
        )
    ]

    rows_by_year = list_tools.group_list_by_key(rows, lambda row: row["review_year"])
    for year, rows_for_year in rows_by_year.items():
        stat_files.append(
            StatFile(
                review_year=str(year),
                total_review_count=len(rows_for_year),
                distributions=distribution_for_rows(rows_for_year),
            )
        )

    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="grade_distributions",
        filename_key=lambda stat_file: stat_file.review_year,
    )
