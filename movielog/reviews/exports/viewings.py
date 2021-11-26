from __future__ import annotations

from datetime import date
from typing import TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger


class Viewing(TypedDict):
    imdb_id: str
    title: str
    year: str
    release_date: date
    viewing_date: date
    viewing_year: str
    sequence: int
    venue: str
    sort_title: str
    slug: str
    grade: str
    genres: list[str]


def fetch_genres(viewing: Viewing) -> list[str]:
    query = """
        SELECT
        genre
        FROM genres
        WHERE movie_imdb_id = "{0}";
    """

    formatted_query = query.format(viewing["imdb_id"])

    return db.fetch_all(formatted_query, lambda cursor, row: row[0])


def export() -> None:
    logger.log("==== Begin exporting {}...", "viewings")

    query = """
        SELECT
            imdb_id
        , title
        , year
        , release_date
        , viewings.date AS viewing_date
        , strftime('%Y', viewings.date) AS viewing_year
        , viewings.sequence
        , viewings.venue
        , sort_title
        , reviews.slug
        , r2.grade
        FROM viewings
        INNER JOIN movies ON viewings.movie_imdb_id = imdb_id
        INNER JOIN release_dates ON release_dates.movie_imdb_id = viewings.movie_imdb_id
        INNER JOIN sort_titles ON sort_titles.movie_imdb_id = viewings.movie_imdb_id
        LEFT JOIN reviews ON viewings.movie_imdb_id = reviews.movie_imdb_id
        LEFT JOIN reviews AS r2 ON viewings.sequence = r2.sequence
        GROUP BY
            viewings.sequence;
        """

    viewings = [
        Viewing(
            imdb_id=row["imdb_id"],
            title=row["title"],
            release_date=row["release_date"],
            viewing_date=row["viewing_date"],
            viewing_year=row["viewing_year"],
            sequence=row["sequence"],
            venue=row["venue"],
            sort_title=row["sort_title"],
            year=row["year"],
            slug=row["slug"],
            grade=row["grade"],
            genres=[],
        )
        for row in db.fetch_all(query)
    ]

    for viewing in viewings:
        viewing["genres"] = fetch_genres(viewing)

    export_tools.serialize_dicts(viewings, "viewings")
