from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Sequence, TypedDict

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger

ETHAN_COEN_IMDB_ID = "nm0001053"


class Stats(Protocol):
    name: str
    slug: str
    title_count: int
    review_count: int
    entity_type: str


@dataclass
class PersonStats(object):
    imdb_id: str
    name: str
    slug: str
    title_count: int
    review_count: int
    entity_type: str


@dataclass
class CollectionStats(object):
    name: str
    slug: str
    title_count: int
    review_count: int
    entity_type: str = "collection"
    imdb_id: Optional[str] = None


class PersonStatRow(TypedDict):
    imdb_id: str
    name: str
    title_count: int
    review_count: int
    slug: str


class CollectionStatRow(TypedDict):
    name: str
    title_count: int
    review_count: int
    slug: str


def _build_collection_stats(row: CollectionStatRow) -> CollectionStats:
    return CollectionStats(
        name=row["name"],
        slug=row["slug"],
        title_count=row["title_count"],
        review_count=row["review_count"],
    )


def _fetch_collection_stats() -> Sequence[CollectionStats]:
    query = """
        SELECT
            collection_name AS 'name'
            , count(movies.imdb_id) AS 'title_count'
            , count(DISTINCT(reviews.movie_imdb_id)) AS 'review_count'
            , watchlist.slug
        FROM watchlist
        LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
        LEFT JOIN reviews ON reviews.movie_imdb_id = watchlist.movie_imdb_id
        WHERE collection_name IS NOT NULL
        GROUP BY
            collection_name
        ORDER BY
            collection_name;
    """

    return [_build_collection_stats(row) for row in db.fetch_all(query)]


def _build_person_stats(row: PersonStatRow, person_type: str) -> PersonStats:
    name = row["name"]
    if row["imdb_id"] == ETHAN_COEN_IMDB_ID:
        name = "The Coen Brothers"

    return PersonStats(
        imdb_id=row["imdb_id"],
        name=name,
        slug=row["slug"],
        title_count=row["title_count"],
        review_count=row["review_count"],
        entity_type=person_type,
    )


def _fetch_person_stats(person_type: str) -> Sequence[PersonStats]:
    query = """
        SELECT
            {0}s.imdb_id AS 'imdb_id'
        , {0}s.full_name AS 'name'
        , count(movies.imdb_id) AS 'title_count'
        , count(DISTINCT(reviews.movie_imdb_id)) AS 'review_count'
        , watchlist.slug
        FROM watchlist
        LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
        LEFT JOIN reviews ON reviews.movie_imdb_id = watchlist.movie_imdb_id
        LEFT JOIN people AS {0}s ON {0}_imdb_id = {0}s.imdb_id
        WHERE {0}_imdb_id IS NOT NULL
        GROUP BY
            {0}_imdb_id
        ORDER BY
            {0}s.full_name;
    """

    return [
        _build_person_stats(person_row, person_type)
        for person_row in db.fetch_all(query.format(person_type))
    ]


def export() -> None:
    logger.log("==== Begin exporting {}...", "watchlist entities")

    stats: list[Stats] = []

    for person_type in ("director", "performer", "writer"):
        stats.extend(_fetch_person_stats(person_type))

    stats.extend(_fetch_collection_stats())

    export_tools.serialize_dataclasses(stats, "watchlist_entities")
