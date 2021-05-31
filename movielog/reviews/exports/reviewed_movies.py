from __future__ import annotations

from typing import Any, TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger


class Person(TypedDict):
    full_name: str


class ReviewedMovie(TypedDict):
    imdb_id: str
    title: str
    original_title: str
    year: str
    review_date: str
    review_sequence: int
    release_date: str
    last_review_grade: str
    last_review_grade_value: float
    slug: str
    sort_title: str
    principal_cast_ids: str
    runtime_minutes: str
    directors: list[Person]
    principal_cast: list[Person]
    countries: list[str]
    aka_titles: list[str]


def person_row_factory(cursor: db.Cursor, row: tuple[Any, ...]) -> Person:
    return Person(full_name=row[0])


def fetch_reviewed_movies() -> list[ReviewedMovie]:
    query = """
        SELECT
        DISTINCT(reviews.movie_imdb_id) AS imdb_id
        , title
        , original_title
        , year
        , reviews.date as review_date
        , strftime('%Y', reviews.date) AS review_year
        , reviews.sequence as review_sequence
        , release_date
        , grade as last_review_grade
        , grade_value as last_review_grade_value
        , slug
        , sort_title
        , principal_cast_ids
        , runtime_minutes
        FROM reviews
        INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
        INNER JOIN release_dates ON reviews.movie_imdb_id = release_dates.movie_imdb_id
        INNER JOIN sort_titles ON reviews.movie_imdb_id = sort_titles.movie_imdb_id
        ORDER BY sort_title ASC;
    """

    return [
        ReviewedMovie(
            imdb_id=row["imdb_id"],
            title=row["title"],
            original_title=row["original_title"],
            year=row["year"],
            review_date=row["review_date"],
            review_sequence=row["review_sequence"],
            release_date=row["release_date"],
            last_review_grade=row["last_review_grade"],
            last_review_grade_value=row["last_review_grade_value"],
            slug=row["slug"],
            sort_title=row["sort_title"],
            principal_cast_ids=row["principal_cast_ids"],
            runtime_minutes=row["runtime_minutes"],
            directors=[],
            principal_cast=[],
            countries=[],
            aka_titles=[],
        )
        for row in db.fetch_all(query)
    ]


def fetch_directors(reviewed_movie: ReviewedMovie) -> list[Person]:
    query = """
        SELECT
        full_name
        FROM people
        INNER JOIN directing_credits ON person_imdb_id = imdb_id
        WHERE movie_imdb_id = "{0}";
    """

    return db.fetch_all(
        query.format(reviewed_movie["imdb_id"]),
        person_row_factory,
    )


def fetch_countries(reviewed_movie: ReviewedMovie) -> list[str]:
    query = """
        SELECT
        country
        FROM countries
        WHERE movie_imdb_id = "{0}";
    """

    return db.fetch_all(
        query.format(reviewed_movie["imdb_id"]), lambda cursor, row: row[0]
    )


def fetch_aka_titles(reviewed_movie: ReviewedMovie) -> list[str]:
    query = """
        SELECT
        title
        FROM aka_titles
        WHERE region = "US"
        AND movie_imdb_id = "{0}"
        AND title != "{1}"
        AND (attributes IS NULL
            OR (attributes NOT LIKE "%working title%"
            AND attributes NOT LIKE "%alternative spelling%"));
    """  # noqa: WPS323

    aka_titles = db.fetch_all(
        query.format(reviewed_movie["imdb_id"], reviewed_movie["title"]),
        lambda cursor, row: row[0],
    )

    if reviewed_movie["original_title"] != reviewed_movie["title"]:
        if reviewed_movie["original_title"] not in aka_titles:
            aka_titles.append(reviewed_movie["original_title"])

    return aka_titles


def fetch_principal_cast(reviewed_movie: ReviewedMovie) -> list[Person]:
    query = """
        SELECT
        full_name
        FROM people
        WHERE imdb_id = "{0}";
    """

    principal_cast = []

    for principal_cast_id in reviewed_movie["principal_cast_ids"].split(","):
        principal_cast.extend(
            db.fetch_all(
                query.format(principal_cast_id),
                person_row_factory,
            )
        )

    return principal_cast


def export() -> None:
    logger.log("==== Begin exporting {}...", "reviewed movies")
    reviewed_movies = []

    for reviewed_movie in fetch_reviewed_movies():
        reviewed_movie["directors"] = fetch_directors(reviewed_movie)
        reviewed_movie["aka_titles"] = fetch_aka_titles(reviewed_movie)
        reviewed_movie["principal_cast"] = fetch_principal_cast(reviewed_movie)
        reviewed_movie["countries"] = fetch_countries(reviewed_movie)

        reviewed_movies.append(reviewed_movie)

    export_tools.serialize_dicts(reviewed_movies, "reviewed_movies")
