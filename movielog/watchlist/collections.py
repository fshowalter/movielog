import json
import os
from dataclasses import dataclass
from glob import glob
from typing import Sequence, TypedDict, cast

from movielog.utils import format_tools
from movielog.utils.logging import logger
from movielog.watchlist import movies, serializer


@dataclass
class Collection(object):
    name: str
    slug: str
    movies: list[movies.Movie]
    folder_name = "collections"


class JsonCollection(TypedDict):
    name: str
    slug: str
    movies: list[movies.JsonMovie]


def deserialize(file_path: str) -> Collection:
    json_collection = None

    with open(file_path, "r") as json_file:
        json_collection = cast(JsonCollection, json.load(json_file))

    return Collection(
        slug=json_collection["slug"],
        name=json_collection["name"],
        movies=movies.deserialize(json_collection["movies"]),
    )


def deserialize_all() -> Sequence[Collection]:
    logger.log(
        "==== Begin reading {} from disk...",
        "watchlist {0}".format(Collection.folder_name),
    )

    file_paths = glob(
        os.path.join(serializer.FOLDER_PATH, Collection.folder_name, "*.json")
    )

    entities = [deserialize(file_path) for file_path in sorted(file_paths)]

    logger.log(
        "Read {} {}.",
        format_tools.humanize_int(len(entities)),
        "watchlist {0}".format(Collection.folder_name),
    )

    return entities
