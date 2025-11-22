from typing import NotRequired, TypedDict


class JsonWatchlistTitleCredit(TypedDict):
    text: NotRequired[str | None]
    attributes: NotRequired[tuple[str] | None]


class JsonWatchlistTitle(TypedDict):
    imdbId: str
    title: str
    titleType: NotRequired[str | None]
    credits: NotRequired[tuple[JsonWatchlistTitleCredit, ...] | None]


class JsonExcludedTitle(TypedDict):
    imdbId: str
    title: str
    titleType: NotRequired[str | None]
    credits: NotRequired[tuple[JsonWatchlistTitleCredit, ...] | None]
    reason: NotRequired[str]
