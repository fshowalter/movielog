from __future__ import annotations

from movielog.exports import (
    list_tools,
    reviewed_titles,
    stats,
    viewings,
    watchlist_titles,
)
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api


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


def export_data() -> None:
    reviews = list_tools.list_to_dict(
        repository_api.reviews(), key=lambda review: review.imdb_id
    )

    titles = list_tools.list_to_dict(
        repository_api.titles(), key=lambda title: title.imdb_id
    )

    titles_with_reviews = [titles[review_id] for review_id in reviews.keys()]

    repository_data = RepositoryData(
        viewings=sorted(
            repository_api.viewings(), key=lambda viewing: viewing.sequence
        ),
        titles=titles,
        reviews=reviews,
        reviewed_titles=titles_with_reviews,
        watchlist_people=build_watchlist_people(),
        watchlist_collections=sorted(
            repository_api.watchlist_collections(),
            key=lambda collection: collection.slug,
        ),
    )

    viewings.export(repository_data)
    reviewed_titles.export(repository_data)
    watchlist_titles.export(repository_data)
    stats.export(repository_data)
