import json
import os
from dataclasses import dataclass
from datetime import date
from glob import glob
from typing import Sequence, TypedDict, cast

from movielog.utils import format_tools
from movielog.utils.logging import logger

FOLDER_NAME = "viewings"


@dataclass
class Viewing(object):
    sequence: int
    date: date
    imdb_id: str
    title: str
    venue: str


class JsonViewing(TypedDict):
    sequence: int
    date: str
    imdb_id: str
    title: str
    venue: str


def deserialize(file_path: str) -> Viewing:
    json_object = None

    with open(file_path, "r") as json_file:
        json_object = cast(JsonViewing, json.load(json_file))

    return Viewing(
        imdb_id=json_object["imdb_id"],
        title=json_object["title"],
        venue=json_object["venue"],
        sequence=json_object["sequence"],
        date=date.fromisoformat(json_object["date"]),
    )


def deserialize_all() -> Sequence[Viewing]:
    logger.log("==== Begin reading {} from disk...", "viewings")

    file_paths = glob(os.path.join(FOLDER_NAME, "*.json"))

    viewings = [deserialize(file_path) for file_path in sorted(file_paths)]

    logger.log("Read {} {}.", format_tools.humanize_int(len(viewings)), "viewings")
    return viewings
