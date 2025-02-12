from typing import TypedDict


class JsonTitle(TypedDict):
    imdbId: str
    title: str


class JsonExcludedTitle(TypedDict):
    imdbId: str
    title: str
    reason: str
