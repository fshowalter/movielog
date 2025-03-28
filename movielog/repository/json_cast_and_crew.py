from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import TypedDict, cast

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "cast-and-crew"


class JsonCastAndCrewMember(TypedDict):
    imdbId: str | list[str]
    name: str
    slug: str


def generate_name_slug(name: str) -> str:
    return slugifier.slugify_name(name)


def generate_file_path(json_name: JsonCastAndCrewMember) -> Path:
    if not json_name["slug"]:
        json_name["slug"] = generate_name_slug(json_name["name"])

    file_name = "{}.json".format(json_name["slug"])
    return Path(FOLDER_NAME) / file_name


def serialize(json_name: JsonCastAndCrewMember) -> None:
    file_path = generate_file_path(json_name)
    path_tools.ensure_file_path(file_path)

    with Path.open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(
            json.dumps(json_name, default=str, indent=2, ensure_ascii=False)
        )

    logger.log(
        "Wrote {}.",
        file_path,
    )


def read_all() -> Iterable[JsonCastAndCrewMember]:
    for file_path in Path(FOLDER_NAME).glob("*.json"):
        with Path.open(file_path) as json_file:
            yield (cast(JsonCastAndCrewMember, json.load(json_file)))
