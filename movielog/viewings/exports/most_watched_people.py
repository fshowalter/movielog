from __future__ import annotations

from collections.abc import Sequence
from typing import TypedDict

from movielog import db
from movielog.utils import list_tools, query_tools

MAX_RESULTS = 10


Person = TypedDict(
    "Person",
    {
        "imdbId": str,
        "fullName": str,
        "viewingCount": int,
        "viewing_sequence_ids": list[int],
    },
)


StatGroup = TypedDict(
    "StatGroup",
    {
        "viewingYear": str,
        "mostWatched": Sequence[Person],
    },
)


class Row(TypedDict):
    viewing_sequence: int
    viewing_year: str
    person_imdb_id: str
    person_full_name: str
    person_slug: str


def fetch_rows(credit_table: str, credit_table_key: str) -> list[Row]:
    query = """
        SELECT
        viewings.sequence AS viewing_sequence
        , strftime('%Y', viewings.date) AS viewing_year
        , person_imdb_id
        , full_name AS person_full_name
        FROM viewings
        LEFT JOIN {0} ON {0}.movie_imdb_id = viewings.movie_imdb_id
        LEFT JOIN people ON person_imdb_id = people.imdb_id
        WHERE
            notes != "(archiveFootage)" AND notes != "(scenesDeleted)" AND {2}
        GROUP BY
            viewing_sequence
            , person_imdb_id
    """

    return db.fetch_all(
        query.format(
            credit_table,
            credit_table_key,
            query_tools.exclude_person_ids_query_clause(),
        )
    )


def most_watched_people_for_rows(rows: list[Row]) -> list[Person]:
    watched_people = []
    rows_by_person_imdb_id = list_tools.group_list_by_key(
        rows, lambda row: row["person_imdb_id"]
    )

    for person_rows in rows_by_person_imdb_id.values():
        if len(person_rows) == 1:
            continue
        first_row = person_rows[0]
        watched_people.append(
            Person(
                imdbId=first_row["person_imdb_id"],
                fullName=first_row["person_full_name"],
                viewingCount=len(person_rows),
                viewing_sequence_ids=[
                    person_row["viewing_sequence"] for person_row in person_rows
                ],
            )
        )

    return sorted(
        watched_people, reverse=True, key=lambda person: person["viewingCount"]
    )[:MAX_RESULTS]


def generate(credit_table: str, credit_table_key: str) -> list[StatGroup]:
    rows = fetch_rows(credit_table, credit_table_key)
    rows_by_review_year = list_tools.group_list_by_key(
        iterable=rows, key=lambda row: row["viewing_year"]
    )
    stat_files = [
        StatGroup(viewingYear="all", mostWatched=most_watched_people_for_rows(rows))
    ]

    for year, rows_for_year in rows_by_review_year.items():
        stat_files.append(
            StatGroup(
                viewingYear=year,
                mostWatched=most_watched_people_for_rows(rows_for_year),
            ),
        )

    return stat_files
