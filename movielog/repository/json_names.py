from __future__ import annotations

import json
import os
from glob import glob
from typing import Iterable, TypedDict, cast

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = os.path.join("data", "names")


JsonName = TypedDict(
    "JsonName",
    {
        "imdbId": str | list[str],
        "name": str,
        "slug": str,
    },
)


def generate_name_slug(name: str) -> str:
    return slugifier.slugify_name(name)


def generate_file_path(json_name: JsonName) -> str:
    if not json_name["slug"]:
        json_name["slug"] = generate_name_slug(json_name["name"])

    file_name = "{0}.json".format(json_name["slug"])
    return os.path.join(FOLDER_NAME, file_name)


def serialize(json_name: JsonName) -> None:
    file_path = generate_file_path(json_name)
    path_tools.ensure_file_path(file_path)

    with open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(
            json.dumps(json_name, default=str, indent=2, ensure_ascii=False)
        )

    logger.log(
        "Wrote {}.",
        file_path,
    )


def read_all() -> Iterable[JsonName]:
    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            yield (cast(JsonName, json.load(json_file)))
