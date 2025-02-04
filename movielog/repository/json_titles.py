from __future__ import annotations

import json
import os
from glob import glob
from typing import Iterable, Optional, TypedDict, cast

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = os.path.join("data", "titles")


JsonWriter = TypedDict(
    "JsonWriter",
    {
        "imdbId": str,
        "name": str,
        "notes": Optional[str],
    },
)

JsonPerformer = TypedDict(
    "JsonPerformer",
    {
        "imdbId": str,
        "name": str,
        "roles": list[str],
    },
)

JsonDirector = TypedDict(
    "JsonDirector",
    {
        "imdbId": str,
        "name": str,
    },
)

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "slug": str,
        "imdbId": str,
        "title": str,
        "originalTitle": str,
        "sortTitle": str,
        "runtimeMinutes": int,
        "year": str,
        "releaseDate": str,
        "countries": list[str],
        "genres": list[str],
        "directors": list[JsonDirector],
        "performers": list[JsonPerformer],
        "writers": list[JsonWriter],
    },
)


def generate_sort_title(title: str, year: str) -> str:
    sort_title = title.lower()
    title_words = sort_title.split(" ")
    lower_words = sort_title.split(" ")
    articles = set(["a", "an", "the"])

    if (len(title_words) > 1) and (lower_words[0] in articles):
        sort_title = " ".join(title_words[1 : len(title_words)])

    return generate_title_slug(sort_title, year)


def generate_title_slug(title: str, year: str) -> str:
    return "{0}-{1}".format(slugifier.slugify_title(title), year)


def generate_file_path(json_title: JsonTitle) -> str:
    if not json_title["slug"]:
        json_title["slug"] = generate_title_slug(
            json_title["title"], json_title["year"]
        )

    file_name = "{0}-{1}.json".format(json_title["slug"], json_title["imdbId"][2:])
    return os.path.join(FOLDER_NAME, file_name)


def serialize(json_title: JsonTitle) -> None:
    file_path = generate_file_path(json_title)
    path_tools.ensure_file_path(file_path)

    with open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(
            json.dumps(json_title, default=str, indent=2, ensure_ascii=False)
        )

    logger.log(
        "Wrote {}.",
        file_path,
    )


def read_all() -> Iterable[JsonTitle]:
    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            yield (cast(JsonTitle, json.load(json_file)))
