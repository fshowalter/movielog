import json
import os
from glob import glob
from typing import Iterable, TypedDict, cast

from movielog.repository import slugifier
from movielog.repository.json_watchlist_titles import JsonTitle
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "collections"

JsonCollection = TypedDict(
    "JsonCollection",
    {
        "name": str,
        "slug": str,
        "titles": list[JsonTitle],
    },
)


def create(name: str) -> JsonCollection:
    new_collection_slug = generate_collection_slug(name)

    existing_collection = next(
        (
            collection
            for collection in read_all()
            if collection["slug"] == new_collection_slug
        ),
        None,
    )

    if existing_collection:
        raise ValueError(
            'Collection with slug "{0}" already exists.'.format(new_collection_slug)
        )

    json_collection = JsonCollection(name=name, slug=new_collection_slug, titles=[])
    serialize(json_collection)
    return json_collection


def add_title(collection_slug: str, imdb_id: str, full_title: str) -> JsonCollection:
    json_collection = next(
        json_collection
        for json_collection in read_all()
        if json_collection["slug"] == collection_slug
    )

    json_collection["titles"].append(JsonTitle(imdbId=imdb_id, title=full_title))

    serialize(json_collection)

    return json_collection


def read_all() -> Iterable[JsonCollection]:
    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            yield (cast(JsonCollection, json.load(json_file)))


def generate_collection_slug(name: str) -> str:
    return slugifier.slugify_name(name)


def generate_file_path(json_collection: JsonCollection) -> str:
    if not json_collection["slug"]:
        json_collection["slug"] = generate_collection_slug(json_collection["name"])

    file_name = "{0}.json".format(json_collection["slug"])
    return os.path.join(FOLDER_NAME, file_name)


def serialize(json_name: JsonCollection) -> None:
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
