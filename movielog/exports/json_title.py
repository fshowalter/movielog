from typing import TypedDict


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    releaseYear: str
    sortTitle: str
    releaseSequence: str
    genres: list[str]
