from __future__ import annotations

import json
import os
from typing import Optional, TypedDict, cast

from movielog.utils import path_tools
from movielog.utils.logging import logger

FILE_NAME = os.path.join("data", "ratings.json")


JsonRating = TypedDict(
    "JsonRating",
    {
        "votes": Optional[int],
        "rating": Optional[float],
    },
)

JsonRatings = TypedDict(
    "JsonRatings",
    {
        "averageImdbVotes": float,
        "averageImdbRating": float,
        "titles": dict[str, JsonRating],
    },
)


def serialize(json_ratings: JsonRatings) -> None:
    path_tools.ensure_file_path(FILE_NAME)

    with open(FILE_NAME, "w") as output_file:
        output_file.write(json.dumps(json_ratings, default=str, indent=2))

    logger.log(
        "Wrote {}.",
        FILE_NAME,
    )


def deserialize() -> JsonRatings:
    with open(FILE_NAME, "r") as json_file:
        return cast(JsonRatings, json.load(json_file))
