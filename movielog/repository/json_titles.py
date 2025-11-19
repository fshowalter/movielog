from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, NotRequired, TypedDict, cast

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = Path("data") / "titles"

type UntypedJson = dict[Any, Any]


class JsonWriter(TypedDict):
    imdbId: str
    name: str
    notes: NotRequired[str]


class JsonPerformer(TypedDict):
    imdbId: str
    name: str
    roles: list[str]
    notes: NotRequired[str]


class JsonDirector(TypedDict):
    imdbId: str
    name: str
    notes: NotRequired[str]


class JsonTitle(TypedDict):
    slug: str
    imdbId: str
    title: str
    originalTitle: str
    sortTitle: str
    runtimeMinutes: int
    year: str
    releaseDate: str
    countries: list[str]
    genres: list[str]
    directors: list[JsonDirector]
    performers: list[JsonPerformer]
    writers: list[JsonWriter]


def generate_sort_title(title: str, year: str) -> str:
    sort_title = title.lower()
    title_words = sort_title.split(" ")
    lower_words = sort_title.split(" ")
    articles = {"a", "an", "the"}

    if (len(title_words) > 1) and (lower_words[0] in articles):
        sort_title = " ".join(title_words[1 : len(title_words)])

    return generate_title_slug(sort_title, year)


def generate_title_slug(title: str, year: str) -> str:
    return f"{slugifier.slugify_title(title)}-{year}"


def generate_file_path(json_title: JsonTitle) -> Path:
    if not json_title["slug"]:
        json_title["slug"] = generate_title_slug(json_title["title"], json_title["year"])

    file_name = "{}-{}.json".format(json_title["slug"], json_title["imdbId"][2:])
    return Path(FOLDER_NAME) / file_name


def serialize(json_title: JsonTitle) -> None:
    file_path = generate_file_path(json_title)
    path_tools.ensure_file_path(file_path)

    with Path.open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(json.dumps(json_title, default=str, indent=2, ensure_ascii=False))

    logger.log(
        "Wrote {}.",
        file_path,
    )


def read_all() -> Iterable[JsonTitle]:
    for file_path in Path(FOLDER_NAME).glob("*.json"):
        with Path.open(file_path) as json_file:
            yield (cast(JsonTitle, json.load(json_file)))
