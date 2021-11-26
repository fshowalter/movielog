from __future__ import annotations

from typing import Optional, TypedDict

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
    original_title: Optional[str]
    principal_cast_ids: str


def fetch_reviewed_movies() -> list[ReviewedMovie]:
    query = """
        SELECT DISTINCT
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


def update_original_title(reviewed_movie: ReviewedMovie) -> None:
    if reviewed_movie["original_title"] == reviewed_movie["title"]:
        reviewed_movie["original_title"] = None


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
        update_original_title(reviewed_movie)
        reviewed_movie["director_names"] = fetch_directors(reviewed_movie)
        reviewed_movie["principal_cast_names"] = fetch_principal_cast(reviewed_movie)
        reviewed_movie["countries"] = fetch_countries(reviewed_movie)
        reviewed_movie.pop("principal_cast_ids")

        reviewed_movies.append(reviewed_movie)

    export_tools.serialize_dicts(reviewed_movies, "reviewed_movies")
