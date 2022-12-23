from __future__ import annotations

from typing import TypedDict

from movielog.reviews import serializer
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger

StatGroup = TypedDict("StatGroup", {"reviewYear": str, "reviewsCreated": int})


def export() -> None:  # noqa: WPS210
    logger.log("==== Begin exporting {}...", "review stats")

    all_reviews = serializer.deserialize_all()

    stat_groups = [
        StatGroup(
            reviewYear="all",
            reviewsCreated=len(all_reviews),
        )
    ]

    reviews_by_year = list_tools.group_list_by_key(
        all_reviews, lambda review: str(review.date.year)
    )
    for year, reviews_for_year in reviews_by_year.items():
        stat_groups.append(
            StatGroup(
                reviewYear=str(year),
                reviewsCreated=len(reviews_for_year),
            )
        )

    export_tools.serialize_dicts_to_folder(
        dicts=stat_groups,
        folder_name="review_stats",
        filename_key=lambda stat_file: stat_file["reviewYear"],
    )
