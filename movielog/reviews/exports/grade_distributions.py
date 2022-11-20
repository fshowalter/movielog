from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger


class Distribution(TypedDict):
    grade: str
    grade_value: int
    review_count: int


class Row(TypedDict):
    review_year: str
    grade_value: int
    grade: str


def fetch_rows() -> list[Row]:
    query = """
        SELECT
        grade
        , grade_value
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

    return sorted(distributions, reverse=True, key=lambda group: group["grade_value"])


def export() -> None:
    logger.log("==== Begin exporting {}...", "grade distributions")
    rows = fetch_rows()

    export_tools.serialize_dicts(distribution_for_rows(rows), "grade_distributions")
