from __future__ import annotations

from typing import Sequence, TypedDict, Union

from movielog import db
from movielog.utils import export_tools
from movielog.utils.logging import logger

JOEL_COEN_IMDB_ID = "nm0001054"


PersonStats = TypedDict(
    "PersonStats",
    {
        "imdbId": str,
        "name": str,
        "slug": str,
        "titleCount": int,
        "entityType": str,
    },
)

CollectionStats = TypedDict(
    "CollectionStats",
    {
        "name": str,
        "slug": str,
        "titleCount": int,
        "entityType": str,
    },
)


def _fetch_collection_stats() -> Sequence[CollectionStats]:
    query = """
        SELECT
            collection_name AS 'name'
            , count(movies.imdb_id) AS 'title_count'
            , watchlist.slug
        FROM watchlist
        LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
        WHERE collection_name IS NOT NULL
        GROUP BY
            collection_name
        ORDER BY
            collection_name;
    """

    return [
        CollectionStats(
            name=row["name"],
            slug=row["slug"],
            titleCount=row["title_count"],
            entityType="collection",
        )
        for row in db.fetch_all(query)
    ]


def _fetch_person_stats(person_type: str) -> Sequence[PersonStats]:
    query = """
        SELECT
            {0}s.imdb_id AS 'imdb_id'
        , {0}s.full_name AS 'name'
        , count(movies.imdb_id) AS 'title_count'
        , watchlist.slug
        FROM watchlist
        LEFT JOIN movies ON watchlist.movie_imdb_id = movies.imdb_id
        LEFT JOIN people AS {0}s ON {0}_imdb_id = {0}s.imdb_id
        WHERE {0}_imdb_id IS NOT NULL
        GROUP BY
            {0}_imdb_id
        ORDER BY
            {0}s.full_name;
    """

    person_stats = []

    for row in db.fetch_all(query.format(person_type)):
        name = row["name"]
        if row["imdb_id"] == JOEL_COEN_IMDB_ID:
            name = "The Coen Brothers"

        person_stats.append(
            PersonStats(
                imdbId=row["imdb_id"],
                name=name,
                slug=row["slug"],
                titleCount=row["title_count"],
                entityType=person_type,
            )
        )

    return person_stats


def export() -> None:
    logger.log("==== Begin exporting {}...", "watchlist entities")

    stats: list[Union[PersonStats, CollectionStats]] = []

    for person_type in ("director", "performer", "writer"):
        stats.extend(_fetch_person_stats(person_type))

    stats.extend(_fetch_collection_stats())

    export_tools.serialize_dicts(stats, "watchlist_entities")
