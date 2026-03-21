from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger


class _JsonCollectionTitle(TypedDict):
    imdbId: str
    title: str
    sortTitle: str
    releaseYear: str
    releaseDate: str
    genres: list[str]
    reviewSlug: str | None


class _JsonCollection(TypedDict):
    name: str
    slug: str
    reviewCount: int
    description: str
    titles: list[_JsonCollectionTitle]


def _build_collection_titles(
    collection: repository_api.Collection, repository_data: RepositoryData
) -> list[_JsonCollectionTitle]:
    titles = []
    for title_id in collection.title_ids:
        title = repository_data.titles[title_id]
        review = repository_data.reviews.get(title_id, None)
        titles.append(
            _JsonCollectionTitle(
                imdbId=title_id,
                title=title.title,
                sortTitle=title.sort_title,
                releaseYear=title.release_year,
                releaseDate=title.release_date,
                genres=title.genres,
                reviewSlug=review.slug if review else None,
            )
        )

    return sorted(titles, key=lambda json_title: json_title["imdbId"])


def export(repository_data: RepositoryData) -> None:
    logger.log("==== Begin exporting {}...", "collections")

    json_collections = []

    for collection in repository_data.collections:
        reviewed_titles = [
            review
            for review in repository_data.reviews.values()
            if review.imdb_id in collection.title_ids
        ]

        json_collections.append(
            _JsonCollection(
                name=collection.name,
                slug=collection.slug,
                reviewCount=len(reviewed_titles),
                titles=_build_collection_titles(collection, repository_data),
                description=collection.description,
            )
        )

    exporter.serialize_dicts_to_folder(
        sorted(
            json_collections,
            key=lambda json_collection: json_collection["name"],
        ),
        "collections",
        filename_key=lambda col: col["slug"],
    )
