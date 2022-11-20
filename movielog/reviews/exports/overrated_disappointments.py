from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger


class Movie(TypedDict, total=False):
    imdb_id: str
    title: str
    year: int
    release_date: str
    slug: str
    sort_title: str
    countries: list[str]
    genres: list[str]
    grade: str


def fetch_movies() -> list[Movie]:
    query = """
        SELECT
            movies.imdb_id
        , movies.title
        , movies.year
        , release_date
        , slug
        , sort_title
        , grade
        , release_date
        FROM reviews
        INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
        INNER JOIN release_dates ON reviews.movie_imdb_id = release_dates.movie_imdb_id
        INNER JOIN sort_titles ON reviews.movie_imdb_id = sort_titles.movie_imdb_id
        GROUP BY
            reviews.movie_imdb_id
        HAVING(movies.votes > (
        SELECT
            avg(votes)
        FROM movies))
        AND (movies.imdb_rating > (
            SELECT
                avg(imdb_rating)
            FROM movies))
        AND (grade LIKE 'F%'
            OR grade LIKE 'D%')
        ORDER BY
            release_date DESC;
    """

    return [
        Movie(
            imdb_id=row["imdb_id"],
            title=row["title"],
            year=row["year"],
            release_date=row["release_date"],
            slug=row["slug"],
            sort_title=row["sort_title"],
            grade=row["grade"],
            genres=[],
        )
        for row in db.fetch_all(query)
    ]


def fetch_genres(movie: Movie) -> list[str]:
    query = """
        SELECT
        genre
        FROM genres
        WHERE movie_imdb_id = "{0}";
    """

    formatted_query = query.format(movie["imdb_id"])

    return db.fetch_all(formatted_query, lambda cursor, row: row[0])


def export() -> None:
    logger.log("==== Begin exporting {}...", "overrated disappointments")
    movies = []

    for movie in fetch_movies():
        movie["genres"] = fetch_genres(movie)

        movies.append(movie)

    export_tools.serialize_dicts(movies, "overrated_disappointments")
