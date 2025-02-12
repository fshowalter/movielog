import datetime
from pathlib import Path
from typing import Any, TypedDict

import yaml

from movielog.repository import markdown_viewings
from movielog.utils import list_tools, path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "viewings-new"


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


def rename_viewings() -> None:
    existing_instances = sorted(
        markdown_viewings.read_all(), key=lambda viewing: viewing["sequence"]
    )

    grouped_viewings = list_tools.group_list_by_key(
        existing_instances, lambda viewing: viewing["date"]
    )

    for viewings in grouped_viewings.values():
        for index, viewing in enumerate(viewings):
            viewing["sequence"] = index + 1
            _serialize(viewing)


def _generate_file_path(markdown_viewing: MarkdownViewing) -> Path:
    file_name = "{}-{:02d}-{}".format(
        markdown_viewing["date"], markdown_viewing["sequence"], markdown_viewing["slug"]
    )

    file_path = Path(FOLDER_NAME) / f"{file_name}.md"

    path_tools.ensure_file_path(file_path)

    return file_path


def _serialize(markdown_viewing: MarkdownViewing) -> Path:
    yaml.add_representer(type(None), _represent_none)

    file_path = _generate_file_path(markdown_viewing)

    with Path.open(file_path, "w") as markdown_file:
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


if __name__ == "__main__":
    rename_viewings()
