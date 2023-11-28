from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from slugify import slugify

from movielog.watchlist.movies import JsonExcludedTitle, JsonMovie, JsonTitle


@dataclass
class Person(object):
    name: str
    slug: str
    imdbId: str
    imdbIds: list[str]
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
