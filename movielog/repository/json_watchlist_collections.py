import json
from typing import Generator, TypedDict, cast

from slugify import slugify

from movielog.repository import watchlist_serializer
from movielog.repository.json_watchlist_titles import JsonTitle

FOLDER_NAME = "collections"

JsonWatchlistCollection = TypedDict(
    "JsonWatchlistCollection",
    {
        "name": str,
        "slug": str,
        "titles": list[JsonTitle],
    },
)


def create(name: str) -> JsonWatchlistCollection:
    new_collection_slug = slugify(name)

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

    json_collection = JsonWatchlistCollection(
        name=name, slug=new_collection_slug, titles=[]
    )
    watchlist_serializer.serialize(json_collection, FOLDER_NAME)
    return json_collection


def add_title(
    collection_slug: str, imdb_id: str, full_title: str
) -> JsonWatchlistCollection:
    json_collection = next(
        json_collection
        for json_collection in read_all()
        if json_collection["slug"] == collection_slug
    )

    json_collection["titles"].append(JsonTitle(imdbId=imdb_id, title=full_title))

    watchlist_serializer.serialize(json_collection, FOLDER_NAME)

    return json_collection


def read_all() -> Generator[JsonWatchlistCollection, None, None]:
    for json_file in watchlist_serializer.read_all(FOLDER_NAME):
        yield (cast(JsonWatchlistCollection, json.load(json_file)))
