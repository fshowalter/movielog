from __future__ import annotations

from datetime import date
from typing import Dict, TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger

JOEL_COEN_IMDB_ID = "nm0001054"

Movie = TypedDict(
    "Movie",
    {
        "imdbId": str,
        "title": str,
        "year": str,
        "sortTitle": str,
        "releaseDate": date,
        "directorImdbIds": list[str],
        "performerImdbIds": list[str],
        "writerImdbIds": list[str],
        "collectionNames": list[str],
    },
)


class Row(TypedDict):
    imdb_id: str
    title: str
    year: str
    release_date: date
    sort_title: str
    director_imdb_id: str
    performer_imdb_id: str
    writer_imdb_id: str
    collection: str


def export() -> None:
    logger.log("==== Begin exporting {}...", "watchlist movies")

    query = """
        SELECT
            movies.imdb_id
        , title
        , year
        , release_date
        , sort_title
        , director_imdb_id
        , performer_imdb_id
        , writer_imdb_id
        , collection_name
        FROM watchlist
        LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
        LEFT JOIN release_dates ON release_dates.movie_imdb_id = movies.imdb_id
        LEFT JOIN sort_titles ON sort_titles.movie_imdb_id = watchlist.movie_imdb_id
        ORDER BY
            release_date ASC
        , movies.imdb_id ASC;
    """

    movies: Dict[str, Movie] = {}

    for row in db.fetch_all(query):
        movie = movies.setdefault(
            row["imdb_id"],
            Movie(
                imdbId=row["imdb_id"],
                title=row["title"],
                year=row["year"],
                sortTitle=row["sort_title"],
                releaseDate=row["release_date"],
                directorImdbIds=[],
                performerImdbIds=[],
                writerImdbIds=[],
                collectionNames=[],
            ),
        )

        if row["director_imdb_id"]:
            movie["directorImdbIds"].append(row["director_imdb_id"])

        if row["performer_imdb_id"]:
            movie["performerImdbIds"].append(row["performer_imdb_id"])

        if row["writer_imdb_id"]:
            movie["writerImdbIds"].append(row["writer_imdb_id"])

        if row["collection_name"]:
            movie["collectionNames"].append(row["collection_name"])

    export_tools.serialize_dicts(list(movies.values()), "watchlist_movies")
