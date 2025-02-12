from collections.abc import Sequence
from typing import Protocol, TypedDict

from movielog.exports import exporter
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger


class WatchlistEntity(Protocol):
    name: str
    slug: str
    title_ids: set[str]


class JsonProgressDetail(TypedDict):
    name: str
    titleCount: int
    reviewCount: int
    slug: str | None


class JsonWatchlistProgress(TypedDict):
    reviewed: int
    total: int
    directorTotal: int
    directorReviewed: int
    directorDetails: list[JsonProgressDetail]
    writerTotal: int
    writerReviewed: int
    writerDetails: list[JsonProgressDetail]
    performerTotal: int
    performerReviewed: int
    performerDetails: list[JsonProgressDetail]
    collectionTotal: int
    collectionReviewed: int
    collectionDetails: list[JsonProgressDetail]


def combined_watchlist_title_ids(repository_data: RepositoryData) -> set[str]:
    watchlist_title_ids = set(
        [
            title_id
            for collection in repository_data.collections
            for title_id in collection.title_ids
        ]
    )

    for person_kind in repository_api.WATCHLIST_PERSON_KINDS:
        for watchlist_person in repository_data.watchlist_people[person_kind]:
            for title_id in watchlist_person.title_ids:
                watchlist_title_ids.add(title_id)

    return watchlist_title_ids


def build_progress_details(
    watchlist_entities: Sequence[WatchlistEntity],
    repository_data: RepositoryData,
) -> list[JsonProgressDetail]:
    entity_progress = []

    for watchlist_entity in watchlist_entities:
        review_ids = watchlist_entity.title_ids.intersection(repository_data.reviews.keys())

        if len(review_ids) == len(watchlist_entity.title_ids):
            continue

        entity_progress.append(
            JsonProgressDetail(
                name=watchlist_entity.name,
                titleCount=len(watchlist_entity.title_ids),
                slug=watchlist_entity.slug if review_ids else None,
                reviewCount=len(review_ids),
            )
        )

    return entity_progress


def watchlist_entity_stats(
    watchlist_entities: Sequence[WatchlistEntity],
    repository_data: RepositoryData,
) -> tuple[int, int]:
    watchlist_entity_title_ids = set(
        [
            title_id
            for watchlist_entity in watchlist_entities
            for title_id in watchlist_entity.title_ids
            if watchlist_entity.title_ids.difference(repository_data.reviews.keys())
        ]
    )

    reviewed_title_ids = watchlist_entity_title_ids.intersection(repository_data.reviews.keys())

    return (len(watchlist_entity_title_ids), len(reviewed_title_ids))


def overall_watchlist_stats(repository_data: RepositoryData) -> tuple[int, int]:
    watchlist_title_ids = combined_watchlist_title_ids(repository_data)

    reviewed_title_ids = watchlist_title_ids.intersection(repository_data.reviews.keys())

    return (len(watchlist_title_ids), len(reviewed_title_ids))


def export(repository_data: RepositoryData) -> None:  # noqa: WPS210
    logger.log("==== Begin exporting {}...", "stats")

    total, reviewed = overall_watchlist_stats(repository_data)

    director_total, director_reviewed = watchlist_entity_stats(
        repository_data.watchlist_people["directors"], repository_data
    )
    performer_total, performer_reviewed = watchlist_entity_stats(
        repository_data.watchlist_people["performers"], repository_data
    )
    writer_total, writer_reviewed = watchlist_entity_stats(
        repository_data.watchlist_people["writers"], repository_data
    )
    collection_total, collection_reviewed = watchlist_entity_stats(
        repository_data.collections, repository_data
    )

    watchlist_progress = JsonWatchlistProgress(
        total=total,
        reviewed=reviewed,
        directorTotal=director_total,
        directorReviewed=director_reviewed,
        directorDetails=build_progress_details(
            repository_data.watchlist_people["directors"], repository_data
        ),
        performerTotal=performer_total,
        performerReviewed=performer_reviewed,
        performerDetails=build_progress_details(
            repository_data.watchlist_people["performers"], repository_data
        ),
        writerTotal=writer_total,
        writerReviewed=writer_reviewed,
        writerDetails=build_progress_details(
            repository_data.watchlist_people["writers"], repository_data
        ),
        collectionTotal=collection_total,
        collectionReviewed=collection_reviewed,
        collectionDetails=build_progress_details(repository_data.collections, repository_data),
    )

    exporter.serialize_dict(watchlist_progress, "watchlist-progress")
