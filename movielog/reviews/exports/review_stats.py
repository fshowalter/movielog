from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from movielog.reviews import serializer
from movielog.reviews.review import Review
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger


@dataclass
class StatGroup(object):
    review_year: str
    reviews_created: int
    watchlist_titles_reviewed: int


def watchlist_titles_reviewed(
    review_iterable: Sequence[Review], watchlist_movie_ids: set[str]
) -> int:
    reviewed_movie_ids = set(review.imdb_id for review in review_iterable)
    return len(watchlist_movie_ids.intersection(reviewed_movie_ids))


def export(watchlist_movie_ids: set[str]) -> None:  # noqa: WPS210
    logger.log("==== Begin exporting {}...", "review stats")

    all_reviews = serializer.deserialize_all()

    stat_groups = [
        StatGroup(
            review_year="all",
            reviews_created=len(all_reviews),
            watchlist_titles_reviewed=watchlist_titles_reviewed(
                all_reviews, watchlist_movie_ids
            ),
        )
    ]

    reviews_by_year = list_tools.group_list_by_key(
        all_reviews, lambda review: str(review.date.year)
    )
    for year, reviews_for_year in reviews_by_year.items():
        stat_groups.append(
            StatGroup(
                review_year=str(year),
                reviews_created=len(reviews_for_year),
                watchlist_titles_reviewed=watchlist_titles_reviewed(
                    reviews_for_year, watchlist_movie_ids
                ),
            )
        )

    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_groups,
        folder_name="review_stats",
        filename_key=lambda stat_file: stat_file.review_year,
    )
