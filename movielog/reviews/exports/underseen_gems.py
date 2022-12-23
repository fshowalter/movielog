from __future__ import annotations

from typing import TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger

Movie = TypedDict(
    "Movie",
    {
        "imdbId": str,
        "title": str,
        "year": int,
        "releaseDate": str,
        "slug": str,
        "sortTitle": str,
        "genres": list[str],
        "grade": str,
        "gradeValue": int,
    },
)


def fetch_underseen_gems() -> list[Movie]:
    query = """
        SELECT
            movies.imdb_id
        , movies.title
        , movies.year
        , release_date
        , slug
        , sort_title
        , grade
        , grade_value
        , release_date
        FROM reviews
        INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
        INNER JOIN release_dates ON reviews.movie_imdb_id = release_dates.movie_imdb_id
        INNER JOIN sort_titles ON reviews.movie_imdb_id = sort_titles.movie_imdb_id
        GROUP BY
            reviews.movie_imdb_id
        HAVING movies.votes < (
        SELECT
            avg(votes)
        FROM movies)
        AND (grade LIKE 'B%'
            OR grade LIKE 'A%')
        ORDER BY
            release_date DESC;
    """

    return [
        Movie(
            imdbId=row["imdb_id"],
            title=row["title"],
            year=row["year"],
            releaseDate=row["release_date"],
            slug=row["slug"],
            sortTitle=row["sort_title"],
            grade=row["grade"],
            gradeValue=row["grade_value"],
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

    formatted_query = query.format(movie["imdbId"])

    return db.fetch_all(formatted_query, lambda cursor, row: row[0])


def export() -> None:
    logger.log("==== Begin exporting {}...", "underseen gems")
    underseen_gems = []

    for movie in fetch_underseen_gems():
        movie["genres"] = fetch_genres(movie)

        underseen_gems.append(movie)

    export_tools.serialize_dicts(underseen_gems, "underseen_gems")
