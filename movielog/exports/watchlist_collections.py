from typing import Optional, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "imdbId": str,
        "title": str,
        "sortTitle": str,
        "year": str,
        "slug": Optional[str],
        "grade": Optional[str],
        "gradeValue": Optional[int],
        "releaseSequence": str,
    },
)

JsonCollection = TypedDict(
    "JsonCollection",
    {
        "name": str,
        "slug": Optional[str],
        "titleCount": int,
        "reviewCount": int,
        "titles": list[JsonTitle],
    },
)


def build_collection_titles(
    collection: repository_api.WatchlistCollection, repository_data: RepositoryData
) -> list[JsonTitle]:
    titles = []
    for title_id in collection.title_ids:
        title = repository_data.titles[title_id]
        review = repository_data.reviews.get(title_id, None)

        titles.append(
            JsonTitle(
                imdbId=title_id,
                title=title.title,
                sortTitle=title.sort_title,
                year=title.year,
                releaseSequence=title.release_sequence,
                slug=review.slug if review else None,
                grade=review.grade if review else None,
                gradeValue=review.grade_value if review else None,
            )
        )

    return titles


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "watchlist-collections")

    watchlist_collections = []

    for collection in repository_data.watchlist_collections:
        reviewed_titles = [
            review
            for review in repository_data.reviews.values()
            if review.imdb_id in collection.title_ids
        ]

        watchlist_collections.append(
            JsonCollection(
                name=collection.name,
                slug=collection.slug if reviewed_titles else None,
                titleCount=len(collection.title_ids),
                reviewCount=len(reviewed_titles),
                titles=build_collection_titles(collection, repository_data),
            )
        )

    exporter.serialize_dicts(
        watchlist_collections,
        "watchlist-collections",
    )
