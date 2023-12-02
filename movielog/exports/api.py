from __future__ import annotations

from movielog.exports import reviewed_titles, stats, viewings, watchlist_titles
from movielog.exports.repository_data import RepositoryData, Watchlist
from movielog.repository import api as repository_api


def build_watchlist() -> Watchlist:
    watchlist: Watchlist = {}

    for watchlist_key in repository_api.WATCHLIST_ENTITY_KINDS:
        watchlist[watchlist_key] = sorted(
            repository_api.watchlist_entities(kind=watchlist_key),
            key=lambda entity: entity.slug,
        )

    return watchlist


def export_data() -> None:
    reviews = list(repository_api.reviews())

    review_ids = set([review.imdb_id for review in reviews])
    titles = list(repository_api.titles())

    titles_with_reviews = [title for title in titles if title.imdb_id in review_ids]

    repository_data = RepositoryData(
        viewings=sorted(
            repository_api.viewings(), key=lambda viewing: viewing.sequence
        ),
        titles=titles,
        reviews=reviews,
        reviewed_titles=titles_with_reviews,
        review_ids=review_ids,
        watchlist=build_watchlist(),
    )

    viewings.export(repository_data)
    reviewed_titles.export(repository_data)
    watchlist_titles.export(repository_data)
    stats.export(repository_data)
