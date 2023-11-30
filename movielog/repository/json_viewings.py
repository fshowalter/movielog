import json
import os
from glob import glob
from typing import Optional, TypedDict, cast

from slugify import slugify

from movielog.repository.data import json_titles
from movielog.utils import format_tools, path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "viewings"

JsonViewing = TypedDict(
    "JsonViewing",
    {
        "sequence": int,
        "date": str,
        "imdb_id": str,
        "slug": str,
        "venue": Optional[str],
        # "venueNotes": Optional[str],
        "medium": Optional[str],
        "medium_notes": Optional[str],
    },
)


def fix() -> None:
    titles = json_titles.deserialize_all()

    for json_viewing in deserialize_all():
        json_viewing["slug"] = next(
            slugify(
                "{0} ({1})".format(title["title"], title["year"]),
                replacements=[("'", "")],
            )
            for title in titles
            if title["imdbId"] == json_viewing["imdb_id"]
        )
        serialize(json_viewing=json_viewing)


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
