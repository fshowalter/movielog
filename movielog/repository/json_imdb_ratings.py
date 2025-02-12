from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict, cast

from movielog.utils import path_tools
from movielog.utils.logging import logger

FILE_NAME = Path("data") / "ratings.json"


class JsonRating(TypedDict):
    votes: int | None
    rating: float | None


class JsonRatings(TypedDict):
    averageImdbVotes: float
    averageImdbRating: float
    titles: dict[str, JsonRating]


def serialize(json_ratings: JsonRatings) -> None:
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
