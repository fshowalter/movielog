from __future__ import annotations

from movielog.exports import reviewed_titles, viewings
from movielog.exports.repository_data import RepositoryData
from movielog.repository import api as repository_api
from movielog.utils import list_tools


def export_data() -> None:
    reviews = list(repository_api.reviews())

    review_ids = set([review.imdb_id for review in reviews])
    titles = list(repository_api.titles())

    titles_with_reviews = [title for title in titles if title.imdb_id in review_ids]
    all_viewings = sorted(
        repository_api.viewings(), key=lambda viewing: viewing.sequence
    )

    repository_data = RepositoryData(
        viewings_for_id=list_tools.group_list_by_key(
            all_viewings, key=lambda viewing: viewing.imdb_id
        ),
        viewings=all_viewings,
        titles=list_tools.list_to_dict(titles, key=lambda title: title.imdb_id),
        reviews=list_tools.list_to_dict(reviews, key=lambda review: review.imdb_id),
        reviewed_titles=titles_with_reviews,
        review_ids=review_ids,
        watchlist={
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
        },
    )

    viewings.export(repository_data)
    reviewed_titles.export(repository_data)
