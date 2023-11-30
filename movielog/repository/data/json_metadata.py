from __future__ import annotations

import json
import os
from statistics import mean
from typing import TypedDict, cast

import imdb

from movielog.repository.datasets import api as datasets_api
from movielog.utils import path_tools
from movielog.utils.logging import logger

imdb_http = imdb.IMDb(reraiseExceptions=True)
FILE_NAME = os.path.join("data", "metadata.json")


JsonMetadata = TypedDict(
    "JsonMetadata",
    {
        "averageImdbVotes": float,
        "averageImdbRating": float,
    },
)


def update(titles: list[datasets_api.DatasetTitle]) -> None:
    average_imdb_rating = mean(
        title["imdb_rating"] for title in titles if title["imdb_rating"]
    )

    average_imdb_votes = mean(
        title["imdb_votes"] for title in titles if title["imdb_votes"]
    )

    json_metadata = JsonMetadata(
        averageImdbRating=average_imdb_rating, averageImdbVotes=average_imdb_votes
    )

    serialize(json_metadata)


def serialize(json_metadata: JsonMetadata) -> None:
    path_tools.ensure_file_path(FILE_NAME)

    with open(FILE_NAME, "w") as output_file:
        output_file.write(json.dumps(json_metadata, default=str, indent=2))

    logger.log(
        "Wrote {}.",
        FILE_NAME,
    )


def deserialize() -> JsonMetadata:
    with open(FILE_NAME, "r") as json_file:
        return cast(JsonMetadata, json.load(json_file))
