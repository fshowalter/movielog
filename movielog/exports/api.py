from __future__ import annotations

from movielog.exports import (
    cast_and_crew,
    collections,
    list_tools,
    overrated_disappointments,
    reviewed_titles,
    stats,
    underseen_gems,
    viewings,
    watchlist_progress,
    watchlist_titles,
)
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils.logging import logger


def build_watchlist_people() -> (
    dict[repository_api.WatchlistPersonKind, list[repository_api.WatchlistPerson]]
):
    watchlist = {}

    for watchlist_key in repository_api.WATCHLIST_PERSON_KINDS:
        watchlist[watchlist_key] = sorted(
            repository_api.watchlist_people(kind=watchlist_key),
            key=lambda entity: entity.slug,
        )

    return watchlist


def export_data() -> None:  # noqa: WPS213
    logger.log("Initializing...")

    repository_api.validate_data()

    reviews = list_tools.list_to_dict(
        repository_api.reviews(), key=lambda review: review.imdb_id
    )

    titles = list_tools.list_to_dict(
        repository_api.titles(), key=lambda title: title.imdb_id
    )

    repository_data = RepositoryData(
        viewings=sorted(
            repository_api.viewings(), key=lambda viewing: viewing.sequence
        ),
        titles=titles,
        reviews=reviews,
        reviewed_titles=[titles[review_id] for review_id in reviews.keys()],
        watchlist_people=build_watchlist_people(),
        watchlist_collections=sorted(
            repository_api.watchlist_collections(),
            key=lambda collection: collection.slug,
        ),
        metadata=repository_api.metadata(),
        names=list(repository_api.names()),
    )

    viewings.export(repository_data)
    reviewed_titles.export(repository_data)
    overrated_disappointments.export(repository_data)
    underseen_gems.export(repository_data)
    watchlist_titles.export(repository_data)
    collections.export(repository_data)
    stats.export(repository_data)
    watchlist_progress.export(repository_data)
    cast_and_crew.export(repository_data)
