from __future__ import annotations

from statistics import mean
from typing import TypedDict, cast

from movielog.repository import json_imdb_ratings, markdown_reviews
from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import api as db_api


class TitleQueryResult(TypedDict):
    imdb_id: str
    imdb_rating: float
    imdb_votes: int


def update_with_db_data(imdb_ids: list[str]) -> None:
    ratings = json_imdb_ratings.deserialize()

    query = """
        SELECT
            imdb_id
        , imdb_rating
        , imdb_votes
        FROM titles
        WHERE imdb_id in ({0});
    """

    quoted_ids = [f'"{imdb_id}"' for imdb_id in imdb_ids]

    title_rows = cast(
        list[TitleQueryResult], db_api.db.fetch_all(query.format(",".join(quoted_ids)))
    )

    assert title_rows

    titles = {}

    for row in title_rows:
        titles[row["imdb_id"]] = json_imdb_ratings.JsonRating(
            votes=row["imdb_votes"], rating=row["imdb_rating"]
        )

    ratings["titles"] = titles

    json_imdb_ratings.serialize(ratings)


def update_for_datasets(
    dataset_titles: list[datasets_api.DatasetTitle],
) -> None:
    average_imdb_votes = mean(title["imdb_votes"] for title in dataset_titles)

    average_imdb_rating = mean(
        title["imdb_rating"]
        for title in dataset_titles
        if title["imdb_votes"] >= average_imdb_votes
    )

    reviewed_title_ids = {review.yaml["imdb_id"] for review in markdown_reviews.read_all()}

    titles = {}

    for dataset_title in dataset_titles:
        if dataset_title["imdb_id"] not in reviewed_title_ids:
            continue

        titles[dataset_title["imdb_id"]] = json_imdb_ratings.JsonRating(
            votes=dataset_title["imdb_votes"], rating=dataset_title["imdb_rating"]
        )

    updated_ratings = json_imdb_ratings.JsonRatings(
        averageImdbRating=average_imdb_rating,
        averageImdbVotes=average_imdb_votes,
        titles=titles,
    )

    json_imdb_ratings.serialize(updated_ratings)
