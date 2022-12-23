from datetime import date
from typing import TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger

Viewing = TypedDict(
    "Viewing",
    {
        "imdbId": str,
        "title": str,
        "year": str,
        "releaseDate": date,
        "viewingDate": date,
        "viewingYear": str,
        "sequence": int,
        "venue": str,
        "medium": str,
        "mediumNotes": str,
        "sortTitle": str,
        "genres": list[str],
    },
)


def fetch_genres(viewing: Viewing) -> list[str]:
    query = """
        SELECT
        genre
        FROM genres
        WHERE movie_imdb_id = "{0}";
    """

    formatted_query = query.format(viewing["imdbId"])

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
        , viewings.medium
        , viewings.medium_notes
        , sort_title
        FROM viewings
        INNER JOIN movies ON viewings.movie_imdb_id = imdb_id
        INNER JOIN release_dates ON release_dates.movie_imdb_id = viewings.movie_imdb_id
        INNER JOIN sort_titles ON sort_titles.movie_imdb_id = viewings.movie_imdb_id
        """

    viewings = [
        Viewing(
            imdbId=row["imdb_id"],
            title=row["title"],
            releaseDate=row["release_date"],
            viewingDate=row["viewing_date"],
            viewingYear=row["viewing_year"],
            sequence=row["sequence"],
            venue=row["venue"],
            medium=row["medium"],
            mediumNotes=row["medium_notes"],
            sortTitle=row["sort_title"],
            year=row["year"],
            genres=[],
        )
        for row in db.fetch_all(query)
    ]

    for viewing in viewings:
        viewing["genres"] = fetch_genres(viewing)

    export_tools.serialize_dicts(viewings, "viewings")
