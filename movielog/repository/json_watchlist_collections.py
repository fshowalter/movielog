import json
from typing import Iterable, TypedDict, cast

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


def read_all() -> Iterable[JsonWatchlistCollection]:
    for json_file in watchlist_serializer.read_all(FOLDER_NAME):
        yield (cast(JsonWatchlistCollection, json.load(json_file)))
