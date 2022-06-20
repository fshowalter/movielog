from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from movielog.reviews import serializer
from movielog.reviews.review import Review
from movielog.utils import export_tools, list_tools
from movielog.utils.logging import logger
from movielog.watchlist import api as watchlist_api


@dataclass
class StatFile(object):
    review_year: str
    total_review_count: int
    average_words_per_review: float
    watchlist_titles_reviewed: int


def count_words_in_markdown(markdown: str) -> int:
    text = markdown

    # Comments
    text = re.sub("<!--(.*?)-->", "", text, flags=re.MULTILINE)
    # Tabs to spaces
    text = text.replace("\t", "    ")
    # More than 1 space to 4 spaces
    text = re.sub("[ ]{2,}", "    ", text)
    # Footnotes
    text = re.sub(r"^\[[^]]*\][^(].*", "", text, flags=re.MULTILINE)
    # Indented blocks of code
    text = re.sub("^( {4,}[^-*]).*", "", text, flags=re.MULTILINE)
    # Custom header IDs
    text = re.sub("{#.*}", "", text)
    # Replace newlines with spaces for uniform handling
    text = text.replace("\n", " ")
    # Remove images
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    # Remove HTML tags
    text = re.sub("</?[^>]*>", "", text)
    # Remove special characters
    text = re.sub(r"[#*`~\-–^=<>+|/:]", "", text)
    # Remove footnote references
    text = re.sub(r"\[[0-9]*\]", "", text)
    # Remove enumerations
    text = re.sub(r"[0-9#]*\.", "", text)

    return len(text.split())


def average_review_length_for_reviews(review_iterable: Sequence[Review]) -> float:
    return sum(
        count_words_in_markdown(str(review.review_content))
        for review in review_iterable
    ) / len(review_iterable)


def watchlist_titles_reviewed(
    review_iterable: Sequence[Review], watchlist_movie_ids: set[str]
) -> int:
    reviewed_movie_ids = set(review.imdb_id for review in review_iterable)
    return len(watchlist_movie_ids.intersection(reviewed_movie_ids))


def export() -> None:  # noqa: WPS210
    logger.log("==== Begin exporting {}...", "review stats")

    all_reviews = serializer.deserialize_all()
    watchlist_movie_ids = watchlist_api.movie_ids()

    stat_files = [
        StatFile(
            review_year="all",
            total_review_count=len(all_reviews),
            average_words_per_review=average_review_length_for_reviews(all_reviews),
            watchlist_titles_reviewed=watchlist_titles_reviewed(
                all_reviews, watchlist_movie_ids
            ),
        )
    ]

    reviews_by_year = list_tools.group_list_by_key(
        all_reviews, lambda review: str(review.date.year)
    )
    for year, reviews_for_year in reviews_by_year.items():
        stat_files.append(
            StatFile(
                review_year=str(year),
                total_review_count=len(reviews_for_year),
                average_words_per_review=average_review_length_for_reviews(
                    reviews_for_year
                ),
                watchlist_titles_reviewed=watchlist_titles_reviewed(
                    reviews_for_year, watchlist_movie_ids
                ),
            )
        )

    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="review_stats",
        filename_key=lambda stat_file: stat_file.review_year,
    )
