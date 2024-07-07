import datetime
import os
import re
from glob import glob
from typing import Any, Iterable, Optional, TypedDict, cast

import yaml

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "viewings"

FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)

MarkdownViewing = TypedDict(
    "MarkdownViewing",
    {
        "sequence": int,
        "date": datetime.date,
        "imdbId": str,
        "slug": str,
        "venue": Optional[str],
        "medium": Optional[str],
        "venueNotes": Optional[str],
        "mediumNotes": Optional[str],
    },
)


def _represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "null")


def create(  # noqa: WPS211
    imdb_id: str,
    date: datetime.date,
    full_title: str,
    medium: Optional[str],
    venue: Optional[str],
    medium_notes: Optional[str],
) -> MarkdownViewing:
    assert medium or venue

    markdown_viewing = MarkdownViewing(
        sequence=_next_sequence(),
        imdbId=imdb_id,
        date=date,
        slug=slugifier.slugify_title(full_title),
        medium=medium,
        venue=venue,
        venueNotes=None,
        mediumNotes=medium_notes,
    )

    _serialize(markdown_viewing)

    return markdown_viewing


def _generate_file_path(markdown_viewing: MarkdownViewing) -> str:
    file_name = "{0:04d}-{1}".format(
        markdown_viewing["sequence"], markdown_viewing["slug"]
    )

    file_path = os.path.join(FOLDER_NAME, "{0}.md".format(file_name))

    path_tools.ensure_file_path(file_path)

    return file_path


def _serialize(markdown_viewing: MarkdownViewing) -> str:
    yaml.add_representer(type(None), _represent_none)

    file_path = _generate_file_path(markdown_viewing)

    with open(file_path, "w") as markdown_file:
        markdown_file.write("---\n")
        yaml.dump(
            markdown_viewing,
            encoding="utf-8",
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            stream=markdown_file,
        )
        markdown_file.write("---\n\n")

    logger.log("Wrote {}.", file_path)

    return file_path


def read_all() -> Iterable[MarkdownViewing]:
    for file_path in glob(os.path.join(FOLDER_NAME, "*.md")):
        with open(file_path, "r") as viewing_file:
            _, frontmatter, _notes = FM_REGEX.split(viewing_file.read(), 2)
            yield cast(MarkdownViewing, yaml.safe_load(frontmatter))


class SequenceError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


def _next_sequence() -> int:
    existing_instances = sorted(read_all(), key=lambda viewing: viewing["sequence"])
    next_sequence_number = len(existing_instances) + 1
    last_instance: Optional[MarkdownViewing] = None

    if next_sequence_number > 1:
        last_instance = existing_instances[-1]

    if last_instance and (last_instance["sequence"] != (next_sequence_number - 1)):
        raise SequenceError(
            "Last item {0} has sequence {1} but next sequence is {2}".format(
                existing_instances[-1:],
                last_instance["sequence"],
                next_sequence_number,
            ),
        )

    return next_sequence_number
