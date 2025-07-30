from typing import TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    sortTitle: str
    year: str
    slug: str | None
    grade: str | None
    gradeValue: int | None
    releaseSequence: str
    reviewSequence: str | None
    reviewDate: str | None


class JsonCollection(TypedDict):
    name: str
    slug: str
    titleCount: int
    reviewCount: int
    titles: list[JsonTitle]
    description: str | None


def build_collection_titles(
    collection: repository_api.Collection, repository_data: RepositoryData
) -> list[JsonTitle]:
    titles = []
    for title_id in collection.title_ids:
        title = repository_data.titles[title_id]
        review = repository_data.reviews.get(title_id, None)
        viewings = sorted(
            (viewing for viewing in repository_data.viewings if viewing.imdb_id == title_id),
            key=lambda title_viewing: title_viewing.sequence,
        )

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
                reviewDate=review.date.isoformat() if review else None,
                reviewSequence=(
                    f"{review.date.isoformat()}-{viewings[0].sequence}"
                    if viewings and review
                    else None
                ),
            )
        )

    return sorted(titles, key=lambda json_title: json_title["releaseSequence"])


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
            JsonCollection(
                name=collection.name,
                slug=collection.slug,
                titleCount=len(collection.title_ids),
                reviewCount=len(reviewed_titles),
                titles=build_collection_titles(collection, repository_data),
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
