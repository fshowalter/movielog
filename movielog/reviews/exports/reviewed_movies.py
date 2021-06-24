from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger


class Person(TypedDict):
    full_name: str


class ReviewedMovie(TypedDict, total=False):
    imdb_id: str
    title: str
    year: int
    release_date: str
    slug: str
    sort_title: str
    runtime_minutes: int
    director_names: list[str]
    principal_cast_names: list[str]
    countries: list[str]
    aka_titles: list[str]
    original_title: str
    principal_cast_ids: str


def fetch_reviewed_movies() -> list[ReviewedMovie]:
    query = """
        SELECT
            reviews.movie_imdb_id AS imdb_id
        , title
        , original_title
        , year
        , release_date
        , slug
        , sort_title
        , principal_cast_ids
        , runtime_minutes
        FROM reviews
        INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
        INNER JOIN release_dates ON reviews.movie_imdb_id = release_dates.movie_imdb_id
        INNER JOIN sort_titles ON reviews.movie_imdb_id = sort_titles.movie_imdb_id
        ORDER BY
            sort_title ASC;
    """

    return [
        ReviewedMovie(
            imdb_id=row["imdb_id"],
            title=row["title"],
            original_title=row["original_title"],
            year=row["year"],
            release_date=row["release_date"],
            slug=row["slug"],
            sort_title=row["sort_title"],
            principal_cast_ids=row["principal_cast_ids"],
            runtime_minutes=row["runtime_minutes"],
            director_names=[],
            principal_cast_names=[],
            countries=[],
            aka_titles=[],
        )
        for row in db.fetch_all(query)
    ]


def fetch_directors(reviewed_movie: ReviewedMovie) -> list[str]:
    query = """
        SELECT
        full_name
        FROM people
        INNER JOIN directing_credits ON person_imdb_id = imdb_id
        WHERE movie_imdb_id = "{0}";
    """

    return db.fetch_all(
        query.format(reviewed_movie["imdb_id"]), lambda cursor, row: row[0]
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


def fetch_principal_cast(reviewed_movie: ReviewedMovie) -> list[str]:
    query = """
        SELECT
        full_name
        FROM people
        WHERE imdb_id = "{0}";
    """

    principal_cast = []

    for principal_cast_id in reviewed_movie["principal_cast_ids"].split(","):
        principal_cast.extend(
            db.fetch_all(query.format(principal_cast_id), lambda cursor, row: row[0])
        )

    return principal_cast


def export() -> None:
    logger.log("==== Begin exporting {}...", "reviewed movies")
    reviewed_movies = []

    for reviewed_movie in fetch_reviewed_movies():
        reviewed_movie["director_names"] = fetch_directors(reviewed_movie)
        reviewed_movie["aka_titles"] = fetch_aka_titles(reviewed_movie)
        reviewed_movie["principal_cast_names"] = fetch_principal_cast(reviewed_movie)
        reviewed_movie["countries"] = fetch_countries(reviewed_movie)
        reviewed_movie.pop("principal_cast_ids")
        reviewed_movie.pop("original_title")

        reviewed_movies.append(reviewed_movie)

    export_tools.serialize_dicts(reviewed_movies, "reviewed_movies")
