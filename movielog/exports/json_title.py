from typing import TypedDict


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    sortTitle: str
    releaseYear: str
    releaseSequence: int
    genres: list[str]
