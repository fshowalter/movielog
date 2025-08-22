from typing import TypedDict


class JsonTitle(TypedDict):
    imdbId: str
    title: str
    releaseYear: str
    titleSequence: int
    releaseSequence: int
    genres: list[str]
