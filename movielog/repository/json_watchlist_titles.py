from typing import NotRequired, TypedDict


class JsonWatchlistTitle(TypedDict):
    imdbId: str
    title: str
    titleType: NotRequired[str | None]
    role: NotRequired[str | None]
    attributes: NotRequired[tuple[str] | None]


class JsonExcludedTitle(TypedDict):
    imdbId: str
    title: str
    titleType: NotRequired[str | None]
    role: NotRequired[str | None]
    attributes: NotRequired[tuple[str] | None]
    reason: NotRequired[str]
