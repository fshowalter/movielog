import json
import os
from dataclasses import asdict
from datetime import date
from glob import glob
from typing import Sequence, TypedDict, cast

from slugify import slugify

from movielog.utils import format_tools, path_tools
from movielog.utils.logging import logger
from movielog.viewings.viewing import Viewing

FOLDER_NAME = "viewings"


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


def generate_file_path(viewing: Viewing) -> str:
    file_name = slugify(
        "{0:04d} {1}".format(viewing.sequence, viewing.title), replacements=[("'", "")]
    )

    file_path = os.path.join(FOLDER_NAME, "{0}.json".format(file_name))

    path_tools.ensure_file_path(file_path)

    return file_path


def serialize(viewing: Viewing) -> str:
    file_path = generate_file_path(viewing)

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps(asdict(viewing), default=str, indent=2))

    logger.log("Wrote {}", file_path)

    return file_path


def deserialize_all() -> Sequence[Viewing]:
    logger.log("==== Begin reading {} from disk...", "viewings")

    file_paths = glob(os.path.join(FOLDER_NAME, "*.json"))

    viewings = [deserialize(file_path) for file_path in sorted(file_paths)]

    logger.log("Read {} {}.", format_tools.humanize_int(len(viewings)), "viewings")
    return viewings
