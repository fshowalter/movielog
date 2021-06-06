from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from typing import TypedDict

from movielog import db
from movielog.utils import list_tools, query_tools

MAX_RESULTS = 20


@dataclass
class Movie(object):
    title: str
    year: int
    slug: str


@dataclass
class Review(object):
    grade_value: float
    date: date
    movie: Movie


@dataclass
class Person(object):
    imdb_id: str
    full_name: str
    slug: str
    average_grade_value: float
    review_count: int
    reviews: list[Review]


@dataclass
class StatFile(object):
    review_year: str
    highest_rated: Sequence[Person]


class Row(TypedDict):
    review_sequence: int
    movie_title: str
    movie_year: int
    movie_imdb_id: str
    person_imdb_id: str
    grade_value: float
    person_full_name: str
    review_date: date
    review_year: str
    person_slug: str
    review_slug: str


def fetch_rows(credit_table: str, credit_table_key: str) -> list[Row]:
    query = """
        SELECT
        reviews.sequence AS review_sequence
        , movies.title AS movie_title
        , movies.year AS movie_year
        , movies.imdb_id AS movie_imdb_id
        , reviews.grade_value
        , person_imdb_id
        , full_name AS person_full_name
        , reviews.date AS review_date
        , strftime('%Y', reviews.date) AS review_year
        , watchlist.slug AS person_slug
        , reviews.slug AS review_slug
        FROM reviews
        LEFT JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
        LEFT JOIN {0} ON {0}.movie_imdb_id = reviews.movie_imdb_id
        LEFT JOIN people ON person_imdb_id = people.imdb_id
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
            reviews.sequence
            , person_imdb_id
    """

    return db.fetch_all(
        query.format(
            credit_table,
            credit_table_key,
            query_tools.exclude_person_ids_query_clause(),
        )
    )


def highest_rated_people_for_rows(rows: list[Row]) -> list[Person]:
    rated_people = []
    rows_by_person_imdb_id = list_tools.group_list_by_key(
        rows, lambda row: row["person_imdb_id"]
    )

    for person_rows in rows_by_person_imdb_id.values():
        first_row = person_rows[0]
        rated_people.append(
            Person(
                imdb_id=first_row["person_imdb_id"],
                full_name=first_row["person_full_name"],
                slug=first_row["person_slug"],
                average_grade_value=sum(row["grade_value"] for row in person_rows)
                / len(person_rows),
                review_count=len(person_rows),
                reviews=[
                    Review(
                        grade_value=person_row["grade_value"],
                        date=person_row["review_date"],
                        movie=Movie(
                            title=person_row["movie_title"],
                            year=person_row["movie_year"],
                            slug=person_row["review_slug"],
                        ),
                    )
                    for person_row in person_rows
                ],
            )
        )

    most_reviews = sorted(
        rated_people, reverse=True, key=lambda person: person.review_count
    )[:MAX_RESULTS]

    return sorted(
        most_reviews, reverse=True, key=lambda person: person.average_grade_value
    )


def generate(credit_table: str, credit_table_key: str) -> list[StatFile]:
    rows = fetch_rows(credit_table, credit_table_key)
    rows_by_review_year = list_tools.group_list_by_key(
        rows, lambda row: row["review_year"]
    )
    stat_files = [
        StatFile(review_year="all", highest_rated=highest_rated_people_for_rows(rows))
    ]

    for year, rows_for_year in rows_by_review_year.items():
        stat_files.append(
            StatFile(
                review_year=year,
                highest_rated=highest_rated_people_for_rows(rows_for_year),
            ),
        )

    return stat_files
