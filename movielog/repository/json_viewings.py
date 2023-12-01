import json
import os
from glob import glob
from typing import Optional, TypedDict, cast

from slugify import slugify

from movielog.utils import format_tools, path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "viewings"

JsonViewing = TypedDict(
    "JsonViewing",
    {
        "sequence": int,
        "date": str,
        "imdbId": str,
        "slug": str,
        "venue": Optional[str],
        "venueNotes": Optional[str],
        "medium": Optional[str],
        "mediumNotes": Optional[str],
    },
)


def deserialize_all() -> list[JsonViewing]:
    logger.log("==== Begin reading {} from disk...", "viewings")
    viewings = []

    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            viewings.append(cast(JsonViewing, json.load(json_file)))

    logger.log("Read {} {}.", format_tools.humanize_int(len(viewings)), "viewings")
    return viewings


def generate_file_path(json_viewing: JsonViewing) -> str:
    file_name = slugify(
        "{0:04d} {1}".format(json_viewing["sequence"], json_viewing["slug"]),
    )

    file_path = os.path.join(FOLDER_NAME, "{0}.json".format(file_name))

    path_tools.ensure_file_path(file_path)

    return file_path


def serialize(json_viewing: JsonViewing) -> str:
    file_path = generate_file_path(json_viewing)

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps(json_viewing, indent=2, default=str))

    logger.log("Wrote {}.", file_path)

    return file_path
