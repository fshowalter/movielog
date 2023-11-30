import json
import os
from collections import defaultdict
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
        "imdbId": str,
        "slug": str,
        "venue": Optional[str],
        "venueNotes": Optional[str],
        "medium": Optional[str],
        "mediumNotes": Optional[str],
    },
)


def fix() -> None:
    # viewings_by_sequence = defaultdict(list)
    titles = json_titles.deserialize_all()
    files_to_rename = []
    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r+") as json_file:
            old_viewing = json.load(json_file)

            # viewings_by_sequence[json_viewing["sequence"]].append(json_viewing)
            new_slug = next(
                title["slug"]
                for title in titles
                if title["imdbId"] == old_viewing["imdb_id"]
            )

            new_viewing = JsonViewing(
                sequence=old_viewing["sequence"],
                date=old_viewing["date"],
                imdbId=old_viewing["imdb_id"],
                slug=new_slug,
                venue=old_viewing["venue"],
                venueNotes=None,
                medium=old_viewing["medium"],
                mediumNotes=old_viewing["medium_notes"],
            )

            correct_file_path = generate_file_path(new_viewing)

            if file_path != correct_file_path:
                files_to_rename.append((file_path, correct_file_path))
                logger.log(
                    "{0} filename should be {1}. Marked for rename.",
                    file_path,
                    correct_file_path,
                )

            json_file.seek(0)
            json_file.write(json.dumps(new_viewing, default=str, indent=2))
            json_file.truncate()
            logger.log(
                "Wrote {}.",
                file_path,
            )

    for old_file_path, new_file_path in files_to_rename:
        os.rename(old_file_path, new_file_path)
        logger.log("{0} renamed to {1}.", old_file_path, new_file_path)
        # serialize(json_viewing=json_viewing)

    # for sequence in viewings_by_sequence.keys():
    #     if len(viewings_by_sequence[sequence]) > 1:
    #         print(sequence)


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
