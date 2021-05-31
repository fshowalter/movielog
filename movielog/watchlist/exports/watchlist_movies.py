from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger

ETHAN_COEN_IMDB_ID = "nm0001053"


@dataclass
class Person(object):
    imdb_id: str
    name: str
    slug: str


@dataclass
class Collection(object):
    name: str
    slug: str


@dataclass
class Movie(object):
    imdb_id: str
    title: str
    year: str
    sort_title: str
    release_date: date
    directors: list[Person]
    performers: list[Person]
    writers: list[Person]
    collections: list[Collection]


class Row(TypedDict):
    imdb_id: str
    title: str
    year: str
    release_date: date
    sort_title: str
    director_imdb_id: str
    director_name: str
    performer_imdb_id: str
    performer_name: str
    writer_imdb_id: str
    writer_name: str
    collection: str
    slug: str


def _build_director_export(row: Row) -> Person:
    name = row["director_name"]
    if row["director_imdb_id"] == ETHAN_COEN_IMDB_ID:
        name = "The Coen Brothers"

    return Person(
        imdb_id=row["director_imdb_id"],
        name=name,
        slug=row["slug"],
    )


def export() -> None:
    logger.log("==== Begin exporting {}...", "watchlist movies")

    query = """
        SELECT
        movies.imdb_id
        , title
        , year
        , release_date
        , sort_title
        , directors.imdb_id AS 'director_imdb_id'
        , directors.full_name AS 'director_name'
        , performers.imdb_id AS 'performer_imdb_id'
        , performers.full_name AS 'performer_name'
        , writers.imdb_id AS 'writer_imdb_id'
        , writers.full_name AS 'writer_name'
        , collection_name AS 'collection'
        , slug
        FROM watchlist
        LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
        LEFT JOIN release_dates ON release_dates.movie_imdb_id = movies.imdb_id
        LEFT JOIN people AS directors ON director_imdb_id = directors.imdb_id
        LEFT JOIN people AS performers ON performer_imdb_id = performers.imdb_id
        LEFT JOIN people AS writers ON writer_imdb_id = writers.imdb_id
        LEFT JOIN sort_titles on sort_titles.movie_imdb_id = watchlist.movie_imdb_id
        ORDER BY
            release_date ASC
        , movies.imdb_id ASC;
    """

    rows: list[Row] = db.fetch_all(query)

    movies: Dict[str, Movie] = {}

    for row in rows:
        movie = movies.setdefault(
            row["imdb_id"],
            Movie(
                imdb_id=row["imdb_id"],
                title=row["title"],
                year=row["year"],
                sort_title=row["sort_title"],
                release_date=row["release_date"],
                directors=[],
                performers=[],
                writers=[],
                collections=[],
            ),
        )

        if row["director_imdb_id"]:
            movie.directors.append(_build_director_export(row))

        if row["performer_imdb_id"]:
            movie.performers.append(
                Person(
                    imdb_id=row["performer_imdb_id"],
                    name=row["performer_name"],
                    slug=row["slug"],
                )
            )

        if row["writer_imdb_id"]:
            movie.writers.append(
                Person(
                    imdb_id=row["writer_imdb_id"],
                    name=row["writer_name"],
                    slug=row["slug"],
                )
            )

        if row["collection"]:
            movie.collections.append(
                Collection(name=row["collection"], slug=row["slug"])
            )

    export_tools.serialize_dataclasses(list(movies.values()), "watchlist_movies")
