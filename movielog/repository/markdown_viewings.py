import datetime
import os
import re
from collections.abc import Iterable
from glob import glob
from typing import Any, TypedDict, cast

import yaml

from movielog.repository import slugifier
from movielog.utils import list_tools, path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "viewings"

FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)


class MarkdownViewing(TypedDict):
    sequence: int
    date: datetime.date
    imdbId: str
    slug: str
    venue: str | None
    medium: str | None
    venueNotes: str | None
    mediumNotes: str | None


def _represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "null")


def create(  # noqa: WPS211
    imdb_id: str,
    date: datetime.date,
    full_title: str,
    medium: str | None,
    venue: str | None,
    medium_notes: str | None,
) -> MarkdownViewing:
    # assert medium or venue

    markdown_viewing = MarkdownViewing(
        sequence=_next_sequence_for_date(date),
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
    file_name = "{0}-{1:02d}-{2}".format(
        markdown_viewing["date"], markdown_viewing["sequence"], markdown_viewing["slug"]
    )

    file_path = os.path.join(FOLDER_NAME, f"{file_name}.md")

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
        with open(file_path) as viewing_file:
            _, frontmatter, _notes = FM_REGEX.split(viewing_file.read(), 2)
            yield cast(MarkdownViewing, yaml.safe_load(frontmatter))


def _next_sequence_for_date(date: datetime.date) -> int:
    existing_instances = sorted(
        read_all(),
        key=lambda viewing: "{0}-{1}".format(viewing["date"], viewing["sequence"]),
    )

    grouped_viewings = list_tools.group_list_by_key(
        existing_instances, lambda viewing: viewing["date"]
    )

    if date not in grouped_viewings.keys():
        return 1

    return len(grouped_viewings[date]) + 1
