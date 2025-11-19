from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import TypedDict, cast

from movielog.utils import path_tools
from movielog.utils.logging import logger

FILE_NAME = Path("data") / "ratings.json"


class JsonRating(TypedDict):
    votes: int
    rating: float


class JsonRatings(TypedDict):
    averageImdbVotes: float
    averageImdbRating: float
    titles: dict[str, JsonRating]


def _update_averages(json_ratings: JsonRatings) -> JsonRatings:
    json_ratings["averageImdbVotes"] = mean(
        title["votes"] for title in json_ratings["titles"].values()
    )

    json_ratings["averageImdbRating"] = mean(
        title["rating"]
        for title in json_ratings["titles"].values()
        if title["votes"] >= json_ratings["averageImdbVotes"]
    )

    return json_ratings


def serialize(json_ratings: JsonRatings) -> None:
    json_ratings = _update_averages(json_ratings)

    path_tools.ensure_file_path(FILE_NAME)

    with Path.open(FILE_NAME, "w") as output_file:
        output_file.write(json.dumps(json_ratings, default=str, indent=2))

    logger.log(
        "Wrote {}.",
        FILE_NAME,
    )


def deserialize() -> JsonRatings:
    with Path.open(FILE_NAME) as json_file:
        return cast(JsonRatings, json.load(json_file))
