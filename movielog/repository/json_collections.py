import json
from collections.abc import Iterable
from pathlib import Path
from typing import TypedDict, cast

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "collections"


class JsonCollectionTitle(TypedDict):
    imdbId: str
    title: str


class JsonCollection(TypedDict):
    name: str
    slug: str
    titles: list[JsonCollectionTitle]
    description: str


def create(name: str, description: str) -> JsonCollection:
    new_collection_slug = _generate_collection_slug(name)

    existing_collection = next(
        (collection for collection in read_all() if collection["slug"] == new_collection_slug),
        None,
    )

    if existing_collection:
        raise ValueError(f'Collection with slug "{new_collection_slug}" already exists.')

    json_collection = JsonCollection(
        name=name, slug=new_collection_slug, titles=[], description=description
    )
    serialize(json_collection)
    return json_collection


def add_title(collection_slug: str, imdb_id: str, full_title: str) -> JsonCollection:
    json_collection = next(
        json_collection
        for json_collection in read_all()
        if json_collection["slug"] == collection_slug
    )

    json_collection["titles"].append(JsonCollectionTitle(imdbId=imdb_id, title=full_title))

    serialize(json_collection)

    return json_collection


def read_all() -> Iterable[JsonCollection]:
    for file_path in Path(FOLDER_NAME).glob("*.json"):
        with Path.open(file_path) as json_file:
            yield (cast(JsonCollection, json.load(json_file)))


def _generate_collection_slug(name: str) -> str:
    return slugifier.slugify_name(name)


def _generate_file_path(json_collection: JsonCollection) -> Path:
    if not json_collection["slug"]:
        json_collection["slug"] = _generate_collection_slug(json_collection["name"])

    file_name = "{}.json".format(json_collection["slug"])
    return Path(FOLDER_NAME) / file_name


def serialize(json_name: JsonCollection) -> None:
    file_path = _generate_file_path(json_name)
    path_tools.ensure_file_path(file_path)

    with Path.open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(json.dumps(json_name, default=str, indent=2, ensure_ascii=False))

    logger.log(
        "Wrote {}.",
        file_path,
    )
