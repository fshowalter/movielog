from __future__ import annotations

from movielog.exports import reviewed_titles, viewings
from movielog.exports.repository_data import RepositoryData, WatchlistDict
from movielog.repository import api as repository_api


def export_data() -> None:
    titles = sorted(repository_api.titles(), key=lambda title: title.sort_title)
    reviews = sorted(
        repository_api.reviews(),
        key=lambda review: review.title(titles).sort_title,
    )

    watchlist: WatchlistDict = {
        "directors": sorted(
            repository_api.watchlist_entities(kind="directors"),
            key=lambda entity: entity.slug,
        ),
        "performers": sorted(
            repository_api.watchlist_entities(kind="performers"),
            key=lambda entity: entity.slug,
        ),
        "writers": sorted(
            repository_api.watchlist_entities(kind="directors"),
            key=lambda entity: entity.slug,
        ),
        "collections": sorted(
            repository_api.watchlist_entities(kind="collections"),
            key=lambda entity: entity.slug,
        ),
    }

    repository_data = RepositoryData(
        viewings=sorted(
            repository_api.viewings(), key=lambda viewing: viewing.sequence
        ),
        titles=titles,
        reviews=reviews,
        watchlist=watchlist,
        review_ids=set(review.imdb_id for review in reviews),
    )

    viewings.export(repository_data)
    reviewed_titles.export(repository_data)
