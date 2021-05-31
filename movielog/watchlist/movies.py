from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TypedDict


@dataclass
class Movie(object):
    title: str
    year: int
    imdb_id: str
    notes: Optional[str] = None


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
        )
        for json_movie in json_movies
    ]
