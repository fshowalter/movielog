from __future__ import annotations

import copy
import json
import operator
import os
import re
from dataclasses import dataclass
from glob import glob
from typing import Sequence, TypedDict, cast

import imdb
from slugify import slugify

from movielog.utils import format_tools
from movielog.utils.logging import logger
from movielog.watchlist import movies, serializer

imdb_http = imdb.IMDb(reraiseExceptions=True)


@dataclass
class Collection(object):
    name: str
    slug: str
    titles: list[movies.JsonTitle]
    folder_name = "collections"


class JsonCollection(TypedDict):
    name: str
    slug: str
    movies: list[movies.JsonMovie]


def add_movie(
    collection: Collection, imdb_id: str, title: str, year: int
) -> Collection:
    collection_copy = copy.deepcopy(collection)

    collection_copy.movies.append(movies.Movie(imdb_id=imdb_id, title=title, year=year))

    collection_copy.movies.sort(key=operator.attrgetter("year"))

    serializer.serialize(collection_copy)

    return collection_copy


def add(name: str) -> Collection:
    slug = slugify(name, replacements=[("'", "")])

    collection = Collection(name=name, slug=slug, movies=[])

    serializer.serialize(collection)

    return collection


def title_sort_key(title: str) -> str:
    year_sort_regex = r"\(\d*\)"

    year = re.search(year_sort_regex, title)

    if year:
        return year.group(0)

    return "(????)"


def update() -> None:
    for collection in deserialize_all():
        for title in collection.titles:
            imdb_movie = imdb_http.get_movie(title["imdbId"][2:])
            title["title"] = imdb_movie["long imdb title"]

        collection.titles = sorted(
            collection.titles, key=lambda title: title_sort_key(title["title"])
        )

        serializer.serialize(collection, collection.folder_name)


def deserialize(file_path: str) -> Collection:
    json_collection = None

    with open(file_path, "r") as json_file:
        json_collection = cast(JsonCollection, json.load(json_file))

    return Collection(
        slug=json_collection["slug"],
        name=json_collection["name"],
        titles=[
            movies.JsonTitle(
                imdbId=json_movie["imdb_id"],
                title=json_movie["title"],
            )
            for json_movie in json_collection["movies"]
        ],
    )


def deserialize_all() -> Sequence[Collection]:
    logger.log(
        "==== Begin reading {} from disk...",
        "watchlist {0}".format(Collection.folder_name),
    )

    file_paths = glob(
        os.path.join(serializer.FOLDER_PATH, Collection.folder_name, "*.json")
    )

    entities = [deserialize(file_path) for file_path in sorted(file_paths)]

    logger.log(
        "Read {} {}.",
        format_tools.humanize_int(len(entities)),
        "watchlist {0}".format(Collection.folder_name),
    )

    return entities
