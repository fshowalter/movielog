from __future__ import annotations

from datetime import date
from typing import Optional, TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger

Person = TypedDict(
    "Person",
    {"fullName": str},
)


ReviewedMovie = TypedDict(
    "ReviewedMovie",
    {
        "imdbId": str,
        "title": str,
        "year": int,
        "releaseDate": str,
        "reviewDate": date,
        "reviewYear": str,
        "slug": str,
        "sortTitle": str,
        "runtimeMinutes": int,
        "directorNames": list[str],
        "principalCastNames": list[str],
        "countries": list[str],
        "originalTitle": Optional[str],
        "principalCastIds": str,
        "grade": str,
        "gradeValue": int,
        "genres": list[str],
    },
)


def fetch_reviewed_movies() -> list[ReviewedMovie]:
    query = """
        SELECT DISTINCT
            reviews.movie_imdb_id AS imdb_id
        , title
        , original_title
        , year
        , date
        , strftime('%Y', reviews.date) AS review_year
        , release_date
        , slug
        , sort_title
        , principal_cast_ids
        , runtime_minutes
        , grade
        , grade_value
        FROM reviews
        INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
        INNER JOIN release_dates ON reviews.movie_imdb_id = release_dates.movie_imdb_id
        INNER JOIN sort_titles ON reviews.movie_imdb_id = sort_titles.movie_imdb_id
        ORDER BY
            sort_title ASC;
    """

    return [
        ReviewedMovie(
            imdbId=row["imdb_id"],
            title=row["title"],
            originalTitle=row["original_title"],
            year=row["year"],
            releaseDate=row["release_date"],
            slug=row["slug"],
            sortTitle=row["sort_title"],
            principalCastIds=row["principal_cast_ids"],
            runtimeMinutes=row["runtime_minutes"],
            directorNames=[],
            principalCastNames=[],
            countries=[],
            grade=row["grade"],
            gradeValue=row["grade_value"],
            reviewDate=row["date"],
            reviewYear=row["review_year"],
            genres=[],
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
        query.format(reviewed_movie["imdbId"]), lambda cursor, row: row[0]
    )


def fetch_countries(reviewed_movie: ReviewedMovie) -> list[str]:
    query = """
        SELECT
        country
        FROM countries
        WHERE movie_imdb_id = "{0}";
    """

    return db.fetch_all(
        query.format(reviewed_movie["imdbId"]), lambda cursor, row: row[0]
    )


def update_original_title(reviewed_movie: ReviewedMovie) -> None:
    if reviewed_movie["originalTitle"] == reviewed_movie["title"]:
        reviewed_movie["originalTitle"] = None


def fetch_genres(reviewed_movie: ReviewedMovie) -> list[str]:
    query = """
        SELECT
        genre
        FROM genres
        WHERE movie_imdb_id = "{0}";
    """

    formatted_query = query.format(reviewed_movie["imdbId"])

    return db.fetch_all(formatted_query, lambda cursor, row: row[0])


def fetch_principal_cast(reviewed_movie: ReviewedMovie) -> list[str]:
    query = """
        SELECT
        full_name
        FROM people
        WHERE imdb_id = "{0}";
    """

    principal_cast = []

    for principal_cast_id in reviewed_movie["principalCastIds"].split(","):
        principal_cast.extend(
            db.fetch_all(query.format(principal_cast_id), lambda cursor, row: row[0])
        )

    return principal_cast


def export() -> None:
    logger.log("==== Begin exporting {}...", "reviewed movies")
    reviewed_movies = []

    for reviewed_movie in fetch_reviewed_movies():
        update_original_title(reviewed_movie)
        reviewed_movie["directorNames"] = fetch_directors(reviewed_movie)
        reviewed_movie["principalCastNames"] = fetch_principal_cast(reviewed_movie)
        reviewed_movie["countries"] = fetch_countries(reviewed_movie)
        reviewed_movie["genres"] = fetch_genres(reviewed_movie)
        export_data = dict(reviewed_movie)
        export_data.pop("principalCastIds")

        reviewed_movies.append(export_data)

    export_tools.serialize_dicts(reviewed_movies, "reviewed_movies")
