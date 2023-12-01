import json
from typing import Iterable, Literal, TypedDict, Union, cast, get_args

from movielog.repository import watchlist_serializer
from movielog.repository.json_watchlist_titles import JsonExcludedTitle, JsonTitle

JsonWatchlistPerson = TypedDict(
    "JsonWatchlistPerson",
    {
        "name": str,
        "slug": str,
        "imdbId": Union[str, list[str]],
        "titles": list[JsonTitle],
        "excludedTitles": list[JsonExcludedTitle],
    },
)

Kind = Literal[
    "directors",
    "writers",
    "performers",
]

KINDS = get_args(Kind)


def read_all(kind: Kind) -> Iterable[JsonWatchlistPerson]:
    for json_file in watchlist_serializer.read_all(kind):
        yield (cast(JsonWatchlistPerson, json.load(json_file)))
