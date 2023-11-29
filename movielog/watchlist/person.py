from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, Union

from slugify import slugify

from movielog.watchlist.movies import JsonExcludedTitle, JsonMovie, JsonTitle


@dataclass
class Person(object):
    fetched: str
    name: str
    slug: str
    imdbId: Union[str, list[str]]
    titles: list[JsonTitle]
    excludedTitles: list[JsonExcludedTitle]


class JsonPerson(TypedDict):
    frozen: bool
    imdb_id: str
    name: str
    slug: str
    movies: list[JsonMovie]


def slug_for_name(name: str) -> str:
    return slugify(name, replacements=[("'", "")])
