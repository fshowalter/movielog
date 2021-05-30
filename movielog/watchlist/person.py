from dataclasses import dataclass
from typing import TypedDict

from slugify import slugify

from movielog.watchlist.movies import JsonMovie, Movie


@dataclass
class Person(object):
    frozen: bool
    name: str
    slug: str
    imdb_id: str
    movies: list[Movie]


class JsonPerson(TypedDict):
    frozen: bool
    imdb_id: str
    name: str
    slug: str
    movies: list[JsonMovie]


def slug_for_name(name: str) -> str:
    return slugify(name, replacements=[("'", "")])
