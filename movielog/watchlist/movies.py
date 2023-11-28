from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TypedDict

JsonTitle = TypedDict("JsonTitle", {"imdbId": str, "title": str})


JsonExcludedTitle = TypedDict(
    "JsonExcludedTitle",
    {
        "imdbId": str,
        "title": str,
        "reason": str,
    },
)


@dataclass
class Movie(object):
    imdb_id: str
    title: str
    notes: str
    year: int


class JsonMovie(TypedDict):
    imdb_id: str
    title: str
    notes: str
    year: int


def deserialize(json_movies: list[JsonMovie]) -> list[Movie]:
    return [
        Movie(
            imdb_id=json_movie["imdb_id"],
            notes=json_movie.get("notes", None),
            title=json_movie["title"],
            year=int(json_movie["year"]),
            kind="",
        )
        for json_movie in json_movies
    ]
