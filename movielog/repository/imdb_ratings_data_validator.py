from __future__ import annotations

from movielog.repository import (
    imdb_ratings_data_updater,
    json_imdb_ratings,
    markdown_reviews,
)


def _get_review_ids() -> set[str]:
    return {review.yaml["imdb_id"] for review in markdown_reviews.read_all()}


def validate() -> None:
    review_ids = _get_review_ids()

    ratings = json_imdb_ratings.deserialize()

    if review_ids.difference(ratings["titles"].keys()):
        imdb_ratings_data_updater.update_with_db_data(list(review_ids))
