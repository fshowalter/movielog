from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import TypedDict

from movielog import db
from movielog.utils import list_tools, query_tools

MAX_RESULTS = 20


@dataclass
class Viewing(object):
    sequence: int
    venue: str
    date: date
    title: str
    year: int
    slug: str


@dataclass
class Person(object):
    imdb_id: str
    full_name: str
    slug: str
    viewing_count: int
    viewings: list[Viewing]


@dataclass
class StatFile(object):
    viewing_year: str
    most_watched: Sequence[Person]


class Row(TypedDict):
    viewing_sequence: int
    movie_title: str
    movie_year: int
    movie_imdb_id: str
    viewing_year: str
    viewing_date: date
    viewing_venue: str
    person_imdb_id: str
    person_full_name: str
    person_slug: str
    review_slug: str


def fetch_rows(credit_table: str, credit_table_key: str) -> list[Row]:
    query = """
        SELECT
        viewings.sequence AS viewing_sequence
        , movies.title AS movie_title
        , movies.year AS movie_year
        , movies.imdb_id AS movie_imdb_id
        , strftime('%Y', viewings.date) AS viewing_year
        , viewings.date AS viewing_date
        , viewings.venue AS viewing_venue
        , person_imdb_id
        , full_name AS person_full_name
        , watchlist.slug AS person_slug
        , reviews.slug AS review_slug
        FROM viewings
        LEFT JOIN movies ON viewings.movie_imdb_id = movies.imdb_id
        LEFT JOIN {0} ON {0}.movie_imdb_id = viewings.movie_imdb_id
        LEFT JOIN people ON person_imdb_id = people.imdb_id
        LEFT JOIN reviews ON viewings.sequence = reviews.sequence
        LEFT JOIN (
            SELECT
                reviews.movie_imdb_id
            , {1}
            , watchlist.slug
            FROM reviews
            INNER JOIN watchlist ON reviews.movie_imdb_id = watchlist.movie_imdb_id
            GROUP BY {1}
        ) AS watchlist ON watchlist.{1} = person_imdb_id
        WHERE {2}
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
        first_row = person_rows[0]
        watched_people.append(
            Person(
                imdb_id=first_row["person_imdb_id"],
                full_name=first_row["person_full_name"],
                slug=first_row["person_slug"],
                viewing_count=len(person_rows),
                viewings=[
                    Viewing(
                        sequence=person_row["viewing_sequence"],
                        venue=person_row["viewing_venue"],
                        date=person_row["viewing_date"],
                        title=person_row["movie_title"],
                        year=person_row["movie_year"],
                        slug=person_row["review_slug"],
                    )
                    for person_row in person_rows
                ],
            )
        )

    return sorted(
        watched_people, reverse=True, key=lambda person: person.viewing_count
    )[:MAX_RESULTS]


def generate(credit_table: str, credit_table_key: str) -> list[StatFile]:
    rows = fetch_rows(credit_table, credit_table_key)
    rows_by_review_year = list_tools.group_list_by_key(
        iterable=rows, key=lambda row: row["viewing_year"]
    )
    stat_files = [
        StatFile(viewing_year="all", most_watched=most_watched_people_for_rows(rows))
    ]

    for year, rows_for_year in rows_by_review_year.items():
        stat_files.append(
            StatFile(
                viewing_year=year,
                most_watched=most_watched_people_for_rows(rows_for_year),
            ),
        )

    return stat_files
